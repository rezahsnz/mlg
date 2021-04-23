const path = require("path");
const dayjs = require("dayjs");
const duration = require("dayjs/plugin/duration");
const { Executor, Task, utils, vm } = require("yajsapi");
const { program } = require("commander");
const fs = require("fs");
const _ = require("lodash");
const { v4: uuidv4 } = require('uuid');

dayjs.extend(duration);

const { asyncWith, logUtils, range } = utils;

const AvailableModels = {
  'densenet121': {
    'image_hash': 'd0e55164c31b55e392a69779169bdb1a7f9f70437570be73ff08e78c',
    'classifier': 'densenet',
  },
  'densenet169': {
    'image_hash': 'd0e55164c31b55e392a69779169bdb1a7f9f70437570be73ff08e78c',
    'classifier': 'densenet',
  },
  'densenet201': {
    'image_hash': 'd0e55164c31b55e392a69779169bdb1a7f9f70437570be73ff08e78c',
    'classifier': 'densenet',
  },
  'nasnet_large': {},
  'nasnet_mobile': {},
  'resnet50': {},
  'resnet101': {},
  'resnet152': {},
  'resnet50v2': {},
  'resnet101v2': {},
  'resnet152v2': {},
  'vgg16': {},
  'vgg19': {},
  'xception': {},
  'inception_v3': {},
  'inception_resnet_v2': {},
}

async function main(model, subnetTag, driver, network) {
  const _package = await vm.repo({
    image_hash: AvailableModels[model]['image_hash'],
    min_mem_gib: 0.5,
    min_storage_gib: 2.0,
  });

  async function* worker(ctx, tasks) {
    const classifier = AvailableModels[model]['classifier']
    ctx.send_file(
      path.join(__dirname, `classifiers/${classifier}.py`),
      '/golem/work/classify.py'
    )    
    for await (let task of tasks) {
      // params.json skeleton:
      // {
      //   model: 'densenet121',
      //   reqs: [
      //     {
      //        id: '34ef21a45....',
      //        image: '9AAAE582'
      //     },
      //      .
      //      .
      //      .
      //     {
      //        id: '21e365002...',
      //        image: '6482CD...'
      //     }
      //   ]
      // }         
      ctx.send_json(
        '/golem/work/params.json',
        {
          'model': model,
          'reqs': task.data() 
        }
      )
      ctx.run(
        '/bin/sh',
        [
          '-c',
          'python3 /golem/work/classify.py > /golem/output/log 2>&1;'
        ]
      )
      let tid = uuidv4()
      const output_file = `out/${pr.id}.json`;
      ctx.download_file(
        `/golem/output/${rid}.json`,
        path.join(__dirname, `./out/${tid}.json`)
      );
      ctx.download_file(
        `/golem/output/log`,
        path.join(__dirname, `./out/${tid}.log`)
      );
      yield ctx.commit({timeout: dayjs.duration({ seconds: 120 }).asMilliseconds()});
      // TODO: Check
      // job results are valid // and reject by:
      // task.reject_task(msg = 'invalid file')
      task.accept_result(output_file);
    }

    ctx.log("done");
    return;
  }
  const req_path = path.join(__dirname, `./reqs/${model}.json`)
  const reqs = JSON.parse(fs.readFileSync(req_path))['reqs']
  // partition requests into arrays of 16 elements so that each node processes
  // 16 images at most: ~32 mb with max 2mb per input image
  const CHUNK_SIZE = 16
  const req_chunks = _.chunk(reqs, CHUNK_SIZE)

  const timeout = dayjs.duration({ minutes: 6 }).asMilliseconds();
  await asyncWith(
    new Executor({
      task_package: _package,
      max_workers: 8,
      timeout: timeout,
      budget: "8.0",
      subnet_tag: subnetTag,
      driver: driver,
      network: network,
      event_consumer: logUtils.logSummary(),
    }),
    async (executor) => {
      for await (let task of executor.submit(
        worker,
        req_chunks.map((rc) => new Task(rc)
      ) {
        console.log("result=", task.result());
      }
    }
  );
  return;
}

program
  .option("--model <model>", "specify model, e.g. densenet121")
  .option("--subnet-tag <subnet>", "set subnet name", "devnet-beta.1")
  .option("--driver <driver>", "payment driver name, for example 'zksync'", "zksync")
  .option("--network <network>", "network name, for example 'rinkeby'", "rinkeby")
  .option("-d, --debug", "output extra debugging");
program.parse(process.argv);
if (program.debug) {
  utils.changeLogLevel("debug");
}
console.log(`Using subnet: ${program.subnetTag}, network: ${program.network}, driver: ${program.driver}`);
main(program.model, program.subnetTag, program.driver, program.network);