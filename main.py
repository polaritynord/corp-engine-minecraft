import corpengine as corp
from corpengine import Entity, Folder, Camera, GlobalScript, ScreenGui, constants
from random import randint

engine = corp.init(windowTitle='Minecraft', flags=corp.flags.SCALED|corp.flags.RESIZABLE)

game = engine.game
window = engine.window
input = game.getService('UserInputService')
obj = game.getService('Object')
assets = game.getService('Assets')
workspace = game.getService('Workspace')
scriptService = engine.game.getService('ScriptService')
guiService = engine.game.getService('GUIService')

class Block(Entity):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)

    def setup(self) -> None:
        self.image = assets.getImage(self.name.lower())

    def update(self, dt: float):
        if input.isCollidingWithMouse(self) and input.isMouseButtonDown('right'):
            obj.remove(self)

class World(Folder):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = 'World'

class Grass(Block):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = 'Grass'

class Dirt(Block):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = 'Dirt'

class Stone(Block):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = 'Stone'

class MainCamera(Camera):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.position = [-80, -500]

class CameraController(GlobalScript):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = 'CameraController'

    def update(self, dt: float) -> None:
        if generationDone:
            speed = 6*dt
            camera = workspace.currentCamera
            mouseRel = input.getMouseRel()
            if camera != None:
                if input.isMouseButtonDown('middle') or input.isMouseButtonDown('left'):
                    camera.position[0] -= mouseRel[0]/2
                    camera.position[1] -= mouseRel[1]/2
                camera.position[0] += input.keyPressed('camera_move_left')*-speed + input.keyPressed('camera_move_right')*speed
                camera.position[1] += input.keyPressed('camera_move_up') * -speed + input.keyPressed('camera_move_down') * speed


class BaseGui(ScreenGui):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = 'UI'

    def setup(self) -> None:
        assets.loadFont('res/fonts/DisposableDroidBB.ttf', 'pixel')
        assets.loadFont('res/fonts/Ubuntu-Medium.ttf', 'ubuntu', 32)

    def update(self) -> None:
        global generationDone
        generationDone = len(workspace.childrenQueue)<1
        if generationDone:
            self.writeText(f'FPS: {engine.window.getFPS()}', [0, 0], 1, corp.colors.BLACK, 'pixel', corp.colors.WHITE)
            self.writeText(f'Block Count: {len(workspace.getChildren())}', [0, 16], 1, corp.colors.BLACK, 'pixel', corp.colors.WHITE)
        else:
            windowSize = constants.DEFAULTSCREENSIZE
            self.drawRect(corp.colors.TAN, corp.Rectangle(0, 0, 640, 360))
            self.writeText('Generating world...', [180, 180], 1, corp.colors.BLACK, 'ubuntu')

def loadAssets() -> None:
    global blocks
    blocks = ['dirt', 'stone', 'grass']
    i = 1
    for block in blocks:
        assets.loadImage(f'res/images/blocks/{block}.png', block)
        print(f'Loading images... ({i}/{len(blocks)})')
        i += 1

def newBlock(type: str, position: list):
    blockTypes: dict = {'grass': Grass(workspace), 'dirt': Dirt(workspace), 'stone': Stone(workspace)}

    newBlock = blockTypes[type]
    newBlock.position = position
    obj.new(newBlock)


def generateChunk(x: int, y: int) -> None:
    height = randint(9, 16)
    x = 0
    y = 0
    for row in range(16):
        for column in range(height - 3):
            newBlock('stone', [x, y])
            y -= 32
        newBlock('dirt', [x, y])
        y -= 32
        newBlock('grass', [x, y])
        x += 32
        y = 0
        height += randint(-1, 1)

def setupInputs() -> None:
    input = engine.game.getService('UserInputService')
    input.addInput('camera_move_left', [corp.K_LEFT])
    input.addInput('camera_move_right', [corp.K_RIGHT])
    input.addInput('camera_move_up', [corp.K_UP])
    input.addInput('camera_move_down', [corp.K_DOWN])


def main() -> None:
    # setting up
    loadAssets()

    global generationDone
    generationDone = False
    generateChunk(0, 0)
    workspace.currentCamera = MainCamera(workspace)
    obj.new(CameraController(scriptService))
    obj.new(BaseGui(guiService))

    setupInputs()
    # mainloop
    engine.window.setTargetFPS(120)
    engine.mainloop()

if __name__ == '__main__':
    main()