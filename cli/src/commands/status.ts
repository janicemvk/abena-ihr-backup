import { Command } from 'commander';
import chalk from 'chalk';
import { execSync } from 'child_process';

export function statusCommand(): Command {
  const cmd = new Command('status')
    .description('Check ABENA node status')
    .option('-b, --base-path <path>', 'Node base path', './abena-data/node')
    .option('-w, --ws-url <url>', 'WebSocket URL for RPC check', 'ws://127.0.0.1:9944')
    .action(async (opts) => {
      console.log(chalk.cyan('ABENA Node Status\n'));

      const basePath = opts.basePath;
      const fs = await import('fs-extra');
      const path = await import('path');

      const chainsPath = path.join(basePath, 'chains', 'development');
      const exists = await fs.pathExists(chainsPath);
      console.log('Data directory: ' + (exists ? chalk.green('exists') : chalk.yellow('not found')));
      console.log('  Path: ' + chainsPath);

      try {
        const ApiPromise = (await import('@polkadot/api')).ApiPromise;
        const WsProvider = (await import('@polkadot/api')).WsProvider;
        const api = await ApiPromise.create({ provider: new WsProvider(opts.wsUrl) });
        const [chain, version, block] = await Promise.all([
          api.rpc.system.chain(),
          api.rpc.system.version(),
          api.rpc.chain.getBlock(),
        ]);
        console.log('\nRPC connection: ' + chalk.green('connected'));
        console.log('  Chain:   ' + String(chain));
        console.log('  Version: ' + String(version));
        const b = block as { block?: { header?: { number?: { toString(): string } } } } | null;
        console.log('  Block:   #' + (b?.block?.header?.number?.toString() ?? '?'));
        await api.disconnect();
      } catch (err) {
        console.log('\nRPC connection: ' + chalk.red('failed'));
        console.log('  URL: ' + opts.wsUrl);
        console.log('  (Is the node running?)');
      }
    });

  return cmd;
}
