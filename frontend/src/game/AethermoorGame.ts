import Phaser from "phaser";
import { PreloadScene } from "./scenes/PreloadScene";
import { WorldScene } from "./scenes/WorldScene";

/**
 * AethermoorGame — Phaser.Game factory.
 *
 * Accepts a parent HTMLElement to mount the canvas into.
 * Scale mode AUTO ensures the game fills the parent div and
 * reacts to window resize. pixelArt mode keeps tile edges crisp
 * without antialiasing.
 *
 * Scenes are registered in order — PreloadScene starts first,
 * generates all textures, then launches WorldScene.
 */
export function createGame(parent: HTMLElement): Phaser.Game {
  const config: Phaser.Types.Core.GameConfig = {
    type: Phaser.AUTO,
    parent,
    width: parent.clientWidth || window.innerWidth,
    height: parent.clientHeight || window.innerHeight,
    backgroundColor: "#0d0d2b",
    pixelArt: true,
    antialias: false,
    scene: [PreloadScene, WorldScene],
    scale: {
      mode: Phaser.Scale.RESIZE,
      autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    input: {
      keyboard: true,
      touch: true,
    },
  };

  return new Phaser.Game(config);
}
