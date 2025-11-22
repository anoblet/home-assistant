declare var process: any;
declare var Buffer: any;
declare var require: any;
declare var module: any;

declare module 'node:fs' {
  const fs: any;
  export = fs;
}

declare module 'node:process' {
  const proc: any;
  export = proc;
}

declare module 'node:timers/promises' {
  export function setTimeout(delay: number): Promise<void>;
}
