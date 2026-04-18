declare module "nipplejs" {
  interface Manager {
    on(event: string, handler: (evt: unknown, data: unknown) => void): void;
    off(event: string, handler: (evt: unknown, data: unknown) => void): void;
    destroy(): void;
  }

  interface Options {
    zone?: HTMLElement;
    color?: string;
    size?: number;
    threshold?: number;
    fadeTime?: number;
    multitouch?: boolean;
    maxNumberOfNipples?: number;
    dataOnly?: boolean;
    position?: { top: string; left: string };
    mode?: "static" | "semi" | "dynamic";
    restJoystick?: boolean;
    catchDistance?: number;
    lockX?: boolean;
    lockY?: boolean;
    catchAngle?: number;
  }

  const nipplejs: {
    create(options?: Options): Manager;
  };

  export default nipplejs;
  export type JoystickManager = Manager;
}