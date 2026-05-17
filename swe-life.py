from cmu_graphics import *
import math
import random

##### FOR GRADERS:

"""
Hello! The following information might be helpful for you as you grade my project:

Key Features:
- Scrolling vertical platformer (THE CLIMB)
    - Urgency system (barbershop/hair reset), gravity tracking
- Progression system
    - Challenges in minigames with difficulty dependent on stats (hygiene, grooming, room)
    - Score on minigames improves stats and gives coins
    - Shop contains items to boost progression
    - THE CLIMB is supposed to be very difficult until stats in all areas are sufficiently high
- 'Angry Birds' item slingshot system (Improve Room)

Grading Shortcuts:
- Press 'o' to toggle dev mode:
    - Press 'h' to improve hygiene, 'g' for grooming, 'r' for room, 'c' for coins
    - Shortens hygiene and room game length considerably
- Press 'p' to toggle demo mode:
    - Will set you to a state about halfway through the game
- Press '[' to toggle OP mode:
    - Will set you to a maxed-out state
    
Below are more detailed descriptions if you want to better understand the minigames/progression system
"""


'''
GAME DESCRIPTION:
This is a game where you are a SWE. You are trying to move up the ranks at your company.
However, you've worked so much that your hygiene has taken a huge hit. If you don't
lock in, you won't go anywhere. To upgrade from
bummyAhh to max level swe, you must play minigames. Each minigame corresponds to the
upgrading of either your hygiene, your grooming, or your room. Completion of minigame
will upgrade the relevant stat and give you coins, which you can use to purchase upgrades in
the shop. You can choose which minigame you want to play, but each minigame will take a chunk of your day, 
moving you from morning, to afternoon, to night, back to morning. 
At any point, you can choose to enter into the climb to try to climb the corporate ladder, which will be a 
scrolling platformer with dangers from the other minigames. Be warned though: there are cleanliness-specific debuffs 
that will make the climb impossible at first.

Your hygiene will affect your vision, as low hygiene will result in a stink cloud covering the screen 
(light green rectangle with opacity based on hygiene).
Your grooming will affect your own jumping, as your excess hair might weigh you down. And your room state
will affect the complexity of the map you are in, as well as your speed. 
The climb will be a scrolling vertical platformer, 
in which you have to avoid dandruff, get bubbles, and reach barbershops! See how high you can climb the
corporate ladder.
'''


'''
THE MINIGAMES:

HYGIENE GAME: 
- Bubbles and dandruff will be falling from the sky. 
- Your goal is to pop the bubbles and avoid the dandruff.
- Associated debuffs: low hygiene = stink cloud screen, low grooming = low jump, more dandruff low room = low speed

GROOMING GAME:
- Your hair is growing! Quickly move your character to randomly spawned barbershops.
- When you reach each barbershop, lava is spawned randomly on the ground.
- The game ends when your hair grows too much or when you hit the lava.
- Associated debuffs: low hygiene = stink cloud screen, faster hair growth rate, low grooming = low jump, low room = more lavas

ROOM GAME:
- You have to sort items in your room into 3 categories on the screen: hamper, trash can, and bookshelf.
- The timer will be quick. Your score is calculated based on the number of correctly sorted items
vs the number of remaining items in your room.
- Associated debuffs: low hygiene = stink cloud screen, low grooming = low jump, low room = low speed

CLIMB GAME:
- You have to jump (or slingshot!) your way up platforms. Watch out though! Dandruff will be falling from the sky,
and your hair will be growing at a great rate. Make sure you avoid the dandruff, don't fall from the platforms,
and make your way to the barbershops that will be floating in the sky
- Associated debuffs: low hygiene = stink cloud screen, faster hair growth rate, low grooming = low jump, more dandruff, low room = low speed
'''

'''
CITATIONS:

- Daniel Ho (me) for art using JSPaint (and trackpad)
- Claude for preliminary minigame ideas (only hygiene game was used)
- Gemini, ChatGPT for low-level debugging (cited in code)

'''

##### COOL FUNCTIONS

def distance(x0, y0, x1, y1):
    return ((x1-x0)**2 + (y1-y0)**2)**0.5


##### CLASSES

class Constants: #put here instead of onAppStart() because i didn't want to have to pass app into every class
    homeGroundY = 260
    gameGroundY = 316
    appWidth = 400
    appHeight = 400
    lowLevel = 33
    midLevel = 66
    highLevel = 90


class Button: #makes the buttons
    def __init__(self, x, y, width, height, text, fill, border = 'black', size = 14):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.fill = fill
        self.border = border
        self.size = size
        self.opacity = 100
    
    def draw(self):
        drawRect(self.x, self.y, self.width, self.height, fill = self.fill, border = self.border)
        centerX = self.x + self.width / 2
        centerY = self.y + self.height / 2
        drawLabel(self.text, centerX, centerY, size=self.size)
        
    def isClicked(self, mouseX, mouseY):
        return (self.x <= mouseX <= self.x + self.width and self.y <= mouseY <= self.y + self.height)

class StatsTracker: #tracks the stats and shi
    def __init__(self, stat):
        self.level = 0
        self.stat = stat
    
    def __repr__(self):
        return f'{self.stat}: {self.level}'
        
    def draw(self, x, y):
        if self.stat == 'hygiene':
            color = 'cyan'
        elif self.stat == 'grooming':
            color = 'pink'
        else:
            color = 'orange'
        widthScale = (self.level+1) * 0.8
        drawRect(x-40, y, widthScale, 12, fill = color, align = 'left')
        drawLabel(f'{self.stat}: {self.level}', x, y)

### SPRITES
class Sprite: #handles all 'sprites'. basically of the items that move on the page
    gravity = 0.5 #g constant
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.onGround = False #how we know whether to turn on gravity or not
        
    def move(self):
        if not self.onGround:
            self.vy += Sprite.gravity #simulates gravity by adding accelerant every tick
        self.x += self.vx
        self.y += self.vy
        
    def ground(self, groundY): #make sure character is on ground
        if self.y >= groundY: #if character is below or at the ground
            self.y = groundY
            self.vy = 0
            self.onGround = True
        else: #if character is in air
            self.onGround = False #just fall down
            
    def isTouching(self, other):
        xMargin = self.width * 0.48 #margin is to make the image accurate to what is drawn. the hitboxes were wonky
        yMargin = self.height * 0.10
        
        left1 = self.x - self.width // 2 + xMargin
        right1 = self.x + self.width // 2 - xMargin
        top1 = self.y - self.height // 2 + yMargin
        bottom1 = self.y + self.height // 2 - yMargin
        
        left2 = other.x - other.width // 2
        right2 = other.x + other.width // 2
        top2 = other.y - other.height // 2
        bottom2 = other.y + other.height // 2
        
        return not (right1 < left2 or left1 > right2 or bottom1 < top2 or top1 > bottom2)

class Character(Sprite): #this is you!
    def __init__(self, x, y, groomingLevel, hygieneLevel, roomLevel, location):
        super().__init__(x, y, 683, 384) #default dimensions given image

        self.hygieneLevel = hygieneLevel
        self.groomingLevel = groomingLevel
        self.roomLevel = roomLevel
        self.location = location
        self.affectedByGravity = False
        self.speed = 2
        self.hairDebuff = 0
    
    
    def getCharacterImage(self):
        if self.groomingLevel <= Constants.lowLevel:
            image = 'cmu://1166263/46487955/very+messy+character.png'
        elif self.groomingLevel <= Constants.midLevel:
            image = 'cmu://1166263/46509676/messy+character.png'
        elif self.groomingLevel <= Constants.highLevel:
            image = 'cmu://1166263/46509687/average+character.png'
        else:
            image = 'cmu://1166263/46509699/clean+character.png'
        return image
    
        
    def draw(self, cameraY=0): #cite AI for cameraY=0 fix for implementation of scrolling platformer
        if self.location == 'home':
            scaleW, scaleH = 1,1
        else:
            scaleW, scaleH = 0.25, 0.25 #makes character smaller for minigames
        image = self.getCharacterImage()
        
        #og charWidth, charHeight = 115, 215
        charW, charH = getImageSize(image)
        self.width, self.height = charW*scaleW, charH*scaleH
        drawY = self.y - cameraY #make sure it is scaled properly
        drawImage(image, self.x, drawY, width = self.width, height = self.height, align = 'center')
        

        opacity = max(0, 90 - self.hygieneLevel) #little stink tendrils
        stinkWidth, stinkHeight = getImageSize('cmu://1166263/46511950/stink.png')
        stinkW, stinkH = stinkWidth//2.4 * scaleW, stinkHeight//2.4 * scaleH
        drawImage('cmu://1166263/46511950/stink.png', self.x - 70*scaleW, drawY-150*scaleH, rotateAngle = 270, opacity = opacity, align = 'center', width = stinkW, height = stinkH)
        drawImage('cmu://1166263/46511950/stink.png', self.x + 110*scaleW, drawY-120*scaleH, opacity = opacity, align = 'center', width = stinkW, height = stinkH)
        
    def move(self, groundY=None): #cite chatgpt for the =None fix to allow for scrolling platformer logic
        super().move()
        self.speed = 2 + max(0, self.roomLevel // 20) #the cleaner the room, the faster you move. fixed softlock issue with max()
        if groundY is not None:    
            self.ground(groundY)
        
        xMargin = self.width * 0.3 #margin is to make the image accurate to what is drawn
        halfWidth = self.width // 2 - xMargin
        if self.x - halfWidth >= Constants.appWidth:
            self.x = -halfWidth
        elif self.x + halfWidth <= 0:
            self.x = Constants.appWidth + halfWidth
            
        
            

class FallingItem(Sprite): #bubbles and dandruff. for hygiene game and the climb
    def __init__(self, x, y, width, height, type):
        super().__init__(x, y, width, height)
        self.type = type
        if type == 'dandruff': #dandruff falls faster
            self.vy = 6
        else:
            self.vy = 3
        
    def move(self): #override! always falls
        self.y += self.vy
        
    def draw(self, cameraY=0):
        if self.type == 'dandruff':
            drawStar(self.x, self.y, self.width / 2, 10, fill = 'gray')
        else: #draw bubble
            drawCircle(self.x, self.y-cameraY, self.width / 2, fill = 'powderBlue')
            drawCircle(self.x + 3, self.y - cameraY - 3, self.width / 6, fill = 'white')
            
class BarberShop(Sprite): #for groom game and the climb
    def __init__(self, x, y):
        super().__init__(x, y, 50, 60)
    
    def draw(self, cameraY=0):
        drawImage('cmu://1166263/46550705/barbershop.png', self.x, self.y-cameraY, align = 'center', fill = 'white')

class Lava(Sprite): #for groom game
    def __init__(self, x, y, width):
        super().__init__(x, y, width, 10)
        
    def draw(self):
        drawRect(self.x, self.y, self.width, self.height, align = 'center', fill = 'red')
    
class RoomItem(Sprite): #for room items
    def __init__(self, x, y, type):
        super().__init__(x, y, 20, 20)
        self.type = type
        self.isThrown = False
        
    def draw(self):
        if self.type == 'clothes':
            url = 'cmu://1166263/46597642/roomItem_clothes.png'
        elif self.type == 'trash':
            url = 'cmu://1166263/46597681/roomItem_trash.png'
        elif self.type == 'book':
            url = 'cmu://1166263/46597703/roomItem_book.png'
        
        drawImage(url, self.x, self.y)
    
class Bin(Sprite): #throw room items in here
    def __init__(self, x, y, type, color, url):
        super().__init__(x, y, 50, 60)
        self.type = type
        self.color = color
        self.url = url
        
    def draw(self):
        drawRect(self.x, self.y, self.width, self.height, align = 'center', fill = self.color, border = 'black')
        drawImage(self.url, self.x, self.y, align = 'center')
        
class Platform(Sprite): #for climb game
    def __init__(self, x, y):
        super().__init__(x, y, 70, 15)
        
    def draw(self, screenY):
        drawRect(self.x, screenY-16, self.width, self.height, align = 'center', fill = 'brown')

###
class Potion: #shop items that boost progression
    def __init__(self, type, price, x, y, fill, imagePath):
        self.type = type
        self.price = price
        self.x = x
        self.y = y
        self.width = 80
        self.height = 200
        self.fill = fill
        self.imagePath = imagePath
    
    def purchase(self, inventory, coins): 
        if self.type not in inventory and self.price <= coins:
            inventory.append(self.type)
            coins -= self.price
            return inventory, coins
        return None, None
        
    def isClicked(self, mouseX, mouseY):
        return self.x <= mouseX <= self.x + self.width and self.y <= mouseY <= self.y + self.height
        
    def draw(self, inventory):
        drawRect(self.x, self.y, self.width, self.height, fill = self.fill, border = 'black', opacity = 70)
        drawLabel(f'{self.price} coins', self.x + 40, self.y + 210, size = 10)
        
        if self.type not in inventory:
            drawImage(self.imagePath, self.x + 40, self.y + 100, align = 'center')
        else:
            drawLabel('Purchased', self.x + 40, self.y + 50, fill = 'red')

### MINIGAMES
            
class Minigame: #base minigame class
    def __init__(self):
        self.active = False

    def start(self, app):
        self.active = True
        self.score = 0
        self.setupCharacter(app, self.groundY)
        
    def setupCharacter(self, app, groundY):
        app.character.location = 'minigame'
        app.character.x = Constants.appWidth // 2
        app.character.y = groundY
        app.character.vx = 0
        app.character.vy = 0
        app.character.onGround = True
        
    def end(self, app):
        self.active = False
        app.scene = 'score'
        
    def getMultiplier(self, app, potionType):
        if potionType in app.inventory:
            return 1.25
        else:
            return 1
            
    def resetCharacterForHome(self, app):
        app.character.location = 'home'
        app.character.x = Constants.appWidth // 2
        app.character.y = Constants.homeGroundY
        app.character.vx = 0
        app.character.vy = 0
        app.timeOfDay += 1
        
    def draw(self, app):
        pass
    def onStep(self, app):
        pass
    def onMousePress(self, app, mouseX, mouseY):
        pass

class ClimbGame(Minigame): #the big game. infinite scrolling platformer
    groundY = Constants.gameGroundY
    
    def start(self, app):
        super().start(app)
        
        app.character.x = Constants.appWidth // 2
        app.character.y = self.groundY
        
        self.cameraY = 200 #worldY for top of the screen
        self.platforms = []
        self.highestReachedY = app.character.y
        
        self.bubblesCollected = 0
        self.dandruffCollected = 0
        self.fallingItems = []
        self.barberShops = []
        self.hairLength = 2
        self.maxHairLength = 45
        
        #low hygiene -> hair grows faster
        hygieneDebuff = max(0, 100 - app.hygiene.level)
        self.hairGrowRate = 0.05 + hygieneDebuff * 0.003
        
        #low grooming -> more dandruff spawns
        groomingDebuff = max(0, 100 - app.grooming.level)
        self.dandruffRate = 0.01 + (groomingDebuff * 0.0005)
        
        self.makePlatforms(app, -400) #draw the platforms up to y=-400. -400 is our target Y so there is always a few extra loaded
        self.platforms.append(Platform(200, 400))#initial platform for character to rest on
        
    def draw(self, app):
        drawImage('cmu://1166263/46638108/climbBackground.png', Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')
        
        drawLabel(f'cameraY: {self.cameraY}', 350, 30) #this was for my sanity but i also think it looks cool so left it
        drawLabel(f'playerY: {app.character.y}', 350, 50)
        
        #hair growth warning - hair turns red when it gets too high
        if self.hairLength >= 30:
            hairColor = 'red'
        else:
            hairColor = 'black'
        drawY = self.worldToScreenY(app.character.y) #places Y in the correct spot
        drawRect(app.character.x, drawY - 8, app.character.width * 0.17, self.hairLength, align = 'bottom', fill = hairColor) #draw hair
        
        app.character.draw(self.cameraY)
        
        #only draw platforms/barbershops if they're on screen
        for platform in self.platforms:
            screenY = self.worldToScreenY(platform.y)
            if -20 <= screenY <= Constants.appHeight + 20: #if the platform is on the screen    
                platform.draw(screenY)
                
        for barberShop in self.barberShops:
            shopScreenY = self.worldToScreenY(barberShop.y)
            if -30 <= shopScreenY <= Constants.appHeight + 30:
                barberShop.draw(self.cameraY)
                
        for item in self.fallingItems:
            item.draw(self.cameraY)
        
        
    def onStep(self, app):
        app.character.onGround = False
        app.character.move()
        self.highestReachedY = min(self.highestReachedY, app.character.y)
        
        self.updateScroller(app)
        
        self.checkDeath(app)
        
        #handle hair/barbershop mechanics. when player touches barbershop, hair length resets
        for i in range(len(self.barberShops)-1,-1,-1):
            barberShop = self.barberShops[i]
            if app.character.isTouching(barberShop):
                self.hairLength = 2
                self.barberShops.remove(barberShop)
                break
        self.hairLength += self.hairGrowRate
        
        #handle dandruff/bubble mechanics. spawn dandruff and bubble at different rates
        if random.random() < self.dandruffRate:
            x = random.randint(20, 380)
            self.fallingItems.append(FallingItem(x, self.cameraY -20, 20, 20, 'dandruff'))
        elif random.random() < 0.03:
            x = random.randint(20, 380)
            self.fallingItems.append(FallingItem(x, self.cameraY - 20, 20, 20, 'bubble'))
       
        
        #update falling items list
        for i in range(len(self.fallingItems)-1, -1 ,-1):
            item = self.fallingItems[i]
            item.move()
            remove = False
            if app.character.isTouching(item):
                if item.type == 'dandruff':
                    self.dandruffCollected += 1
                else:
                    self.bubblesCollected += 1
                remove = True
            if self.worldToScreenY(item.y) >= Constants.appHeight:
                remove = True
            if remove:
                self.fallingItems.remove(item)
        
    
    def checkDeath(self, app): #end game if player falls or hair length gets too long
        if app.character.y - self.cameraY > Constants.appHeight: #if player falls below camera view
            self.end(app)
        elif self.hairLength >= self.maxHairLength:
            self.end(app)
    
    #houses scrolling logic. triggers platform generation, moves camera, lets player land
    def updateScroller(self, app):
        playerScreenY = self.worldToScreenY(app.character.y)
        targetY = self.cameraY - 400
        self.makePlatforms(app, targetY)
        self.checkPlatformCollisions(app)
        if playerScreenY < Constants.appHeight // 2: #if player is in top half of map, move camera up
            self.cameraY = app.character.y - 150 #-150 allows buffer for player to fall a little
    
    #lands player on platform if they are falling    
    def checkPlatformCollisions(self, app):
        for platform in self.platforms:
            if app.character.isTouching(platform):
                yMargin = app.character.height * .1 #jank but because of the weird image hitbox
                playerBottom = app.character.y + app.character.height / 2 - yMargin
                platformTop = platform.y - platform.height / 2
                if app.character.vy > 0 and playerBottom >= platformTop and playerBottom - app.character.vy <= platformTop + 15: #character is falling, overlapping platform, and was above platform last frame. +15 is buffer
                    app.character.vy = 0
                    app.character.y = platformTop - app.character.height / 2 + yMargin
                    app.character.onGround = True
                    break #no need to check other platforms
    
    def findHighestPlatformY(self, platforms):
        highest = platforms[0].y
        for platform in platforms:
            if platform.y < highest:
                highest = platform.y
        return highest
    
    def makePlatforms(self, app, targetY):
        if self.platforms == []:
            highestY = Constants.appHeight #our current highest platform is at the bottom of the map
        else:
            highestY = self.findHighestPlatformY(self.platforms) #finds our current highest platform
        
        while highestY > targetY: # while the highest current platform is lower than our target
            newY = highestY - random.randint(70, 120) #new platform will be 70-120px higher
            newScreenY = self.worldToScreenY(newY) #affects where we place it on the screen
            newX = random.randint(30, Constants.appWidth - 30)
            self.platforms.append(Platform(newX, newY))
            
            #also make the barbershops
            if len(self.platforms) % 4 == 0:
                barberShopX = random.randint(30, Constants.appWidth - 30)
                self.barberShops.append(BarberShop(barberShopX, newY - 55))
            
            highestY = newY
        
    #the biggest the baddest helper function. converts worldY coordinate to screenY
    def worldToScreenY(self, worldY):
        return worldY - self.cameraY
        
    #calculates score and stuff
    def end(self, app):
        super().end(app)
        self.score = math.floor(-self.highestReachedY + self.bubblesCollected * 10 - self.dandruffCollected * 20) + 316 #+316 bc player spawns immediately at -316
        self.active = False
        app.scene = 'finalScore'
        if app.activeMinigame.score > app.highScore:
            app.highScore = app.activeMinigame.score
            app.newHigh = True
        else:
            app.newHigh = False
        self.resetCharacterForHome(app)

## HYGIENE
class HygieneGame(Minigame):
    groundY = Constants.gameGroundY
    
    def start(self, app):
        super().start(app)
        self.timer = app.stepsPerSecond * app.minigameLength #15 seconds
        self.fallingItems = []
        
        groomingDebuff = max(0, 100 - app.room.level)
        self.dandruffRate = 0.01 + (groomingDebuff * 0.0005)
        
        
    def draw(self, app):
        drawImage('cmu://1166263/46516287/hygiene.png', Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')
        drawLabel(f'Score: {self.score}', 350, 30)
        drawLabel(f'Seconds left: {self.timer // app.stepsPerSecond}', 350, 50)
        app.character.draw()
        for item in self.fallingItems:
            item.draw()
            
    def end(self, app):
        super().end(app)
        self.resetCharacterForHome(app)
        
    def onStep(self, app):
        self.timer -= 1
        app.character.move(self.groundY)
        
        if random.random() < self.dandruffRate: #checks every frame, 5% chance
            x = random.randint(20, 380)
            self.fallingItems.append(FallingItem(x, 0, 20, 20, 'dandruff'))
        elif random.random() < 0.03:
            x = random.randint(20, 380)
            self.fallingItems.append(FallingItem(x, 0, 20, 20, 'bubble'))
        
        #gemini cite - helped debug error when item was touched at the same time as it touched the ground
        for i in range(len(self.fallingItems)-1, -1 ,-1):
            item = self.fallingItems[i]
            item.move()
            remove = False
            if app.character.isTouching(item):
                if item.type == 'dandruff':
                    self.score -= 5
                else:
                    self.score += 5
                remove = True
            if item.y >= self.groundY:
                remove = True
            if remove:
                self.fallingItems.remove(item)
            
        if self.timer <= 0:
            self.end(app)
        

        
    def end(self, app):
        super().end(app)
        
        self.resetCharacterForHome(app)
        hmultiplier = self.getMultiplier(app, 'hygiene')
        cmultiplier = self.getMultiplier(app, 'coin')
        app.hygiene.level += math.floor(self.score*hmultiplier)
        app.coins += math.floor((self.score *cmultiplier/ 4))  ## change these to adapt with score


##GROOMING
class GroomingGame(Minigame):
    groundY = Constants.gameGroundY

    def start(self, app):
        super().start(app)
        
        
        self.hairLength = 2
        self.barberShop = BarberShop(20, 306)
        self.lavaList = []
        self.maxHairLength = 80
        hygieneDebuff = max(0, 100 - app.hygiene.level)
        self.hairGrowRate = 0.3 + hygieneDebuff * 0.003
        roomDebuff = max(0, 100 - app.room.level)
        self.numLavas = 3 + roomDebuff//25 #7 lavas to start
        
        for i in range(self.numLavas):
            self.lavaList.append(Lava(i*75, 342, 20))
        
        
    def draw(self, app):
        drawImage('cmu://1166263/46516560/grooming.png', Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')
        drawLabel(f'Score: {self.score}', 350, 30)
        
        #draw hair
        if self.hairLength >= 60:
            hairColor = 'red'
        else:
            hairColor = 'black'
        drawRect(app.character.x, app.character.y - 8, app.character.width * 0.17, self.hairLength, align = 'bottom', fill = hairColor) #draw hair
        
        app.character.draw()
        self.barberShop.draw()
        for lava in self.lavaList:
            lava.draw()
        

        
    def onStep(self, app):
        self.hairLength += self.hairGrowRate
        app.character.move(self.groundY)
        if self.hairLength >= self.maxHairLength:
            self.end(app)
        if app.character.isTouching(self.barberShop):
            oldBarberX = self.barberShop.x
            
            newBarberX = random.randint(20, 380)
            self.barberShop = BarberShop(newBarberX, 306)
            self.hairLength = 2
            self.score += 5
            
            #reset lavas
            self.lavaList = []
            for i in range(self.numLavas):
                newLavaX = random.randint(20, 380)
                while abs(newLavaX - oldBarberX) < 50: #make sure lava's a far enough distance from barbershop
                    newLavaX = random.randint(20, 380)
                self.lavaList.append(Lava(newLavaX, 342, 20))
            
        for lava in self.lavaList:
            if app.character.isTouching(lava):
                self.end(app)


        
    def end(self, app):
        super().end(app)
        self.resetCharacterForHome(app)
        gmultiplier = self.getMultiplier(app, 'grooming')
        cmultiplier = self.getMultiplier(app, 'coin')
        app.grooming.level += math.floor(self.score*gmultiplier)
        app.coins += math.floor((self.score*cmultiplier/4))  

##ROOM 
class RoomGame(Minigame):
    groundY = Constants.gameGroundY
    
    def start(self, app):
        super().start(app)
        self.types = ['clothes', 'trash', 'book']
        self.timer = app.stepsPerSecond * app.minigameLength #15 seconds
        self.currentItem = self.spawnItem(app)
        
        self.isAiming = False
        self.aimCurX = 0
        self.aimCurY = 0
        self.itemX = self.currentItem.x
        self.itemY = self.currentItem.y
        self.throwPower = 0.18
        app.character.x = 100

        self.bins = [
            Bin(255, self.groundY-9, 'clothes', 'lightPink', 'cmu://1166263/46597642/roomItem_clothes.png'),
            Bin(315, self.groundY-9, 'trash', 'gray', 'cmu://1166263/46597681/roomItem_trash.png'),
            Bin(375, self.groundY-9, 'book', 'tan', 'cmu://1166263/46597703/roomItem_book.png')]
        
    def spawnItem(self, app):
        itemType = self.types[random.randint(0,2)]
        return RoomItem(app.character.x, app.character.y, itemType)
        
        
    def draw(self, app):
        drawImage('cmu://1166263/46516563/room.png', Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')
        drawLabel(f'Score: {self.score}', 350, 30)
        drawLabel(f'Seconds left: {self.timer // app.stepsPerSecond}', 350, 50)
        
        app.character.draw()
        self.currentItem.draw()
        
        for bin in self.bins:
            bin.draw()
        
        if self.isAiming and not self.currentItem.isThrown:
            self.drawAngryBirdsAimer(app)
    
    def drawAngryBirdsAimer(self, app):
        
        #+15 and -10 are to situate aimer at item loc
        dx = app.character.x + 15 - self.aimCurX
        dy = app.character.y -10- self.aimCurY
        
        simVx = dx * self.throwPower
        simVy = dy * self.throwPower
        
        simX = self.itemX
        simY = self.itemY
        
        for frame in range(25): #this will simulate 25 frames in the future
            simVy += Sprite.gravity
            simX += simVx
            simY += simVy
            
            if simY >= self.groundY:
                break
            
            drawCircle(simX, simY, 2, fill = 'white')
            
        
        
    def onStep(self, app):
        self.timer -= 1
        app.character.move(self.groundY)
        
        if self.currentItem.isThrown:
            self.currentItem.move()
            if self.currentItem.y >= self.groundY:
                self.currentItem = self.spawnItem(app)
                return
            
            for bin in self.bins:
                if self.currentItem.isTouching(bin):
                    if self.currentItem.type == bin.type:
                        self.score += 15
                    else:
                        self.score -= 5
                    self.currentItem = self.spawnItem(app)
                    break
                
        else:
            
            self.itemX = app.character.x + 15
            self.itemY = app.character.y - 10
            
            self.currentItem.x = self.itemX
            self.currentItem.y = self.itemY
            
            
        if self.timer <= 0:
            self.end(app)
            
    def onMousePress(self, app, mouseX, mouseY):
        if not self.currentItem.isThrown:
            self.isAiming = True
            self.aimCurX = mouseX
            self.aimCurY = mouseY
        
    def onMouseDrag(self, app, mouseX, mouseY):
        if self.isAiming:
            self.aimCurX = mouseX
            self.aimCurY = mouseY
    
    def onMouseRelease(self, app, mouseX, mouseY):
        if self.isAiming:
            self.isAiming = False
            self.currentItem.isThrown = True
            
            #basically, the direction is opposite of where the mouse is relative to the item location. makes it a slingshot
            dx = app.character.x + 15 - mouseX
            dy = app.character.y - 10 - mouseY
            
            badddAim = 0 #i got rid of this feature after playtesting but i think it's still pretty cool
            # badddAim = max(0, (50-app.grooming.level) / 20) #the worse the aim, the further off the throw
            
            #sets velocity for thrown item. item will launch in the above direction. throwPower scales it cuz otherwise it go way too far
            self.currentItem.vx = dx*self.throwPower + random.uniform(-badddAim, badddAim)
            self.currentItem.vy = dy*self.throwPower + random.uniform(-badddAim, badddAim)
        
    def end(self, app):
        super().end(app)
        self.resetCharacterForHome(app)
        rmultiplier = self.getMultiplier(app, 'room')
        cmultiplier = self.getMultiplier(app, 'coin')
        app.room.level += math.floor(self.score*rmultiplier)
        app.coins += math.floor(self.score*cmultiplier/4)  ## change these to adapt with score



############# APP SECTION ################

# app.scene = home, shop, minigame, score, information

##### DRAW
def onAppStart(app):
    app.width = Constants.appWidth
    app.height = Constants.appHeight
    app.stepsPerSecond = 60 #change??
    app.minigameLength = 15
    app.homeButtons = [
        Button(10, 10, 70, 70, 'Shop', 'yellow'),
        Button(140, 10, 120, 70, 'CLIMB', 'red', size = 16),
        Button(10, 345, 120, 50, 'Improve Hygiene', 'cyan'),
        Button(140, 345, 120, 50, 'Improve Grooming', 'pink', size = 13),
        Button(270, 345, 120, 50, 'Improve Room', 'orange', size = 13)
    ]
    app.goHomeShop = Button(10, 10, 70, 70, 'Home', 'lightGray')
    app.goHomeScore = Button(125, 275, 150, 50, 'Back to Home', 'white')
    app.highScore = 0
    app.startHomeButton = Button(125, 250, 150, 50, 'BEGIN', 'limeGreen', size = 16)
    app.startGameButton = Button(125, 320, 150, 50, 'START', 'limeGreen', size = 16)
    
    
    resetApp(app)
    
def resetApp(app):
    app.inGame = False
    app.devMode = False
    app.scene = 'information'
    app.hygiene = StatsTracker('hygiene')
    app.grooming = StatsTracker('grooming')
    app.room = StatsTracker('room')
    app.infoScene = 'title'
    app.coins = 0
    app.timeOfDay = 0 #based on %. 0=morning, 1=afternoon, 2=evening
    app.gameOver = False
    app.character = Character(Constants.appWidth // 2, Constants.homeGroundY, app.grooming.level, app.hygiene.level, app.room.level, 'home')
    app.inventory = []
    app.demoMode = False
    app.OPMode = False
    app.newHigh = False
    resetPots(app)
    
    app.hygieneGame = HygieneGame()
    app.groomingGame = GroomingGame()
    app.roomGame = RoomGame()
    app.climbGame = ClimbGame()
    app.activeMinigame = None
    
def resetPots(app):
    app.hygienePot = Potion('hygiene', 20, 10, 110, 'cyan', 'cmu://1166263/46512182/hygiene+pot.png')
    app.groomingPot = Potion('grooming', 20, 110, 110, 'pink', 'cmu://1166263/46512254/groom+pot.png')
    app.roomPot = Potion('room', 20, 210, 110, 'orange', 'cmu://1166263/46512270/room+pot.png')
    app.coinPot = Potion('coin', 30, 310, 110, 'yellow', 'cmu://1166263/46512282/coin+pot.png')
    app.shopItems = [app.hygienePot, app.groomingPot, app.roomPot, app.coinPot]
    

def redrawAll(app):
    drawScene(app)

def drawScene(app):
    if app.scene == 'information':
        drawInformation(app, app.infoScene)
    elif app.scene == 'home':
        drawHome(app)
    elif app.scene == 'shop':
        drawShop(app)
    elif app.scene == 'minigame':
        drawMinigame(app)
    elif app.scene == 'score':
        drawScore(app)
    elif app.scene == 'finalScore':
        drawFinalScore(app)

### INFORMATION
def drawInformation(app, scene):
    drawImage('cmu://1166263/46516282/score_info.png', Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')
    
    if scene == 'title':
        drawHomeInfo(app)
        app.startHomeButton.draw()
    else:
        if scene == 'hygiene':
            drawHygieneInfo(app)
        elif scene == 'grooming':
            drawGroomingInfo(app)
        elif scene == 'room':
            drawRoomInfo(app)
        elif scene == 'climb':
            drawClimbInfo(app)
        app.startGameButton.draw()
        
def drawHomeInfo(app):
    drawLabel('WELCOME to SWE Life!', Constants.appWidth // 2, 60, size = 24, bold = True)
    drawLabel('You are a software engineer trying to climb the ', Constants.appWidth // 2, 100, size = 16)
    drawLabel("the corporate ladder. Unfortunately, you've worked", Constants.appWidth // 2, 120, size = 16)
    drawLabel('so hard, your hygiene and environment have tanked!', Constants.appWidth // 2, 140, size = 16)
    
    drawLabel('Play minigames to upgrade your stats, then ENTER', Constants.appWidth // 2, 180, size = 16)
    drawLabel('the climb. Warning: low stats = impossible climb.', Constants.appWidth // 2, 200, size = 16)
    

def drawHygieneInfo(app):
    drawLabel('HYGIENE MINIGAME', Constants.appWidth // 2, 60, size = 24, bold = True)
    drawLabel('Pop the falling bubbles and avoid the dandruff!', Constants.appWidth // 2, 100, size = 16)
    
    drawLabel('Current debuffs:', Constants.appWidth // 2, 140, bold = True, size = 18)
    
    #Associated debuffs: low hygiene = stink cloud screen, low grooming = low jump, more dandruff low room = low speed
    if app.hygiene.level <= 40:
        drawLabel(f'Your hygiene level is low, at {app.hygiene.level}.', Constants.appWidth // 2, 170, size = 16)
        drawLabel('It is generating a stink cloud obscuring your vision.', Constants.appWidth // 2, 190, size = 16)
    if app.grooming.level <= 40:
        drawLabel(f'Your grooming level is low, at {app.grooming.level}.', Constants.appWidth // 2, 220, size = 16)
        drawLabel('Your hair is weighing you down and making more dandruff.', Constants.appWidth // 2, 240, size = 15)
    if app.room.level <= 40:
        drawLabel(f'Your room level is low, at {app.room.level}.', Constants.appWidth // 2, 270, size = 16)
        drawLabel('You have to move slowly around all of the clutter.', Constants.appWidth // 2, 290, size = 16)
    
def drawGroomingInfo(app):
    drawLabel('GROOMING MINIGAME', Constants.appWidth // 2, 60, size = 24, bold = True)
    drawLabel('Your hair is growing! Get to the barbershops but avoid the lava.', Constants.appWidth // 2, 100, size = 14)
    
    drawLabel('Current debuffs:', Constants.appWidth // 2, 140, bold = True, size = 18)
    
    #Associated debuffs: low hygiene = stink cloud screen and faster hair growth, low grooming = low jump, low room = low speed and more lava
    if app.hygiene.level <= 40:
        drawLabel(f'Your hygiene level is low, at {app.hygiene.level}.', Constants.appWidth // 2, 170, size = 16)
        drawLabel('It is generating a stink cloud and growing your hair faster.', Constants.appWidth // 2, 190, size = 15)
    if app.grooming.level <= 40:
        drawLabel(f'Your grooming level is low, at {app.grooming.level}.', Constants.appWidth // 2, 220, size = 16)
        drawLabel('Your hair is weighing you down, lowering your jump.', Constants.appWidth // 2, 240, size = 16)
    if app.room.level <= 40:
        drawLabel(f'Your room level is low, at {app.room.level}.', Constants.appWidth // 2, 270, size = 16)
        drawLabel('You move slower and more lava spawns.', Constants.appWidth // 2, 290, size = 16)
    

def drawRoomInfo(app):
    drawLabel('ROOM MINIGAME', Constants.appWidth // 2, 60, size = 24, bold = True)
    drawLabel('Sort the items. Click and drag to aim! (Aim like Angry Birds)', Constants.appWidth // 2, 100, size = 14)
    
    drawLabel('Current debuffs:', Constants.appWidth // 2, 140, bold = True, size = 18)
    
    #Associated debuffs: low hygiene = stink cloud screen, low grooming = low jump, low room = low speed
    if app.hygiene.level <= 40:
        drawLabel(f'Your hygiene level is low, at {app.hygiene.level}.', Constants.appWidth // 2, 170, size = 16)
        drawLabel('It is generating a stink cloud obscuring your vision.', Constants.appWidth // 2, 190, size = 16)
    if app.grooming.level <= 40:
        drawLabel(f'Your grooming level is low, at {app.grooming.level}.', Constants.appWidth // 2, 220, size = 16)
        drawLabel('Your hair is weighing you down, lowering your jump.', Constants.appWidth // 2, 240, size = 16)
    if app.room.level <= 40:
        drawLabel(f'Your room level is low, at {app.room.level}.', Constants.appWidth // 2, 270, size = 16)
        drawLabel('You have to move slowly around all of the clutter.', Constants.appWidth // 2, 290, size = 16)

def drawClimbInfo(app):
    drawLabel('THE CLIMB', Constants.appWidth // 2, 60, size = 24, bold = True)
    drawLabel('Climb up the corporate ladder, but watch out!', Constants.appWidth // 2, 95, size = 14)
    drawLabel('Dandruff, your hair, and gravity are all after you.', Constants.appWidth // 2, 117.5, size = 14)
    
    
    drawLabel('Current debuffs:', Constants.appWidth // 2, 140, bold = True, size = 18)
    
    #Associated debuffs: low hygiene = stink cloud screen, faster hair growth rate, low grooming = low jump, more dandruff, low room = low speed
    if app.hygiene.level <= 40:
        drawLabel(f'Your hygiene level is low, at {app.hygiene.level}.', Constants.appWidth // 2, 170, size = 16)
        drawLabel('It is generating a stink cloud and growing your hair faster.', Constants.appWidth // 2, 190, size = 15)
    if app.grooming.level <= 40:
        drawLabel(f'Your grooming level is low, at {app.grooming.level}.', Constants.appWidth // 2, 220, size = 16)
        drawLabel('Your jump is lowered and more dandruff spawns.', Constants.appWidth // 2, 240, size = 16)
    if app.room.level <= 40:
        drawLabel(f'Your room level is low, at {app.room.level}.', Constants.appWidth // 2, 270, size = 16)
        drawLabel('You have to move slowly around all of the clutter.', Constants.appWidth // 2, 290, size = 16)


### HOME
def drawHome(app):
    
    drawHomeBG(app)
    displayStats(app)
    drawCharacter(app)
    drawHomeButtons(app)

def drawHomeBG(app):

    #set to right image
    if app.room.level <= Constants.lowLevel:
        roomImage = 'cmu://1166263/46511791/very+messy+home.png'
    elif app.room.level <= Constants.midLevel:
        roomImage = 'cmu://1166263/46511533/messy+home.png'
    elif app.room.level <= Constants.highLevel:
        roomImage = 'cmu://1166263/46511369/average+home.png'
    else:
        roomImage = 'cmu://1166263/46510814/clean+home.png'
       
    drawRect(0, 0, app.width, app.height, fill = 'lightGray')
    drawImage(roomImage, Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')   
    drawWindows(app)

def drawWindows(app):
    if app.timeOfDay % 3 == 0:
        windowColor = 'lightSkyBlue'
    elif app.timeOfDay % 3 == 1:
        windowColor = 'steelBlue'
    else:
        windowColor = 'navy'
    
    drawRect(100, 150, 80, 80, fill = windowColor, align = 'center')
    drawLine(100, 110, 100, 190, fill = 'white', lineWidth = 3)
    drawLine(60, 150, 140, 150, fill = 'white', lineWidth = 3)
    drawLine(58, 190, 142, 190, fill = 'brown', lineWidth = 5)
    drawRect(300, 150, 80, 80, fill = windowColor, align = 'center')
    drawLine(300, 110, 300, 190, fill = 'white', lineWidth = 3)
    drawLine(260, 150, 340, 150, fill = 'white', lineWidth = 3)
    drawLine(258, 190, 342, 190, fill = 'brown', lineWidth = 5)
    
def displayStats(app):
    app.hygiene.draw(350, 15)
    app.grooming.draw(350, 35)
    app.room.draw(350, 55)
    if app.scene == 'home':    
        drawLabel(f'coins: {app.coins}', 350, 75)
    #add a timeOfDay tracker?

def drawCharacter(app):
    app.character.groomingLevel = app.grooming.level
    app.character.hygieneLevel = app.hygiene.level
    app.character.roomLevel = app.room.level
    app.character.draw()

def drawHomeButtons(app):
    for button in app.homeButtons:
        button.draw()

### SHOP

def drawShop(app):
    drawShopBG(app)
    drawItems(app)
    drawHomeButton(app)
    displayStats(app)
    
    
def drawShopBG(app):
    drawRect(0, 0, app.width, app.height, fill = 'yellow')
    drawImage('cmu://1166263/46510529/shop+bg.png',Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')
    drawLabel(f'Coins: {app.coins}', Constants.appWidth // 2, 50, size = 20)
    drawLabel('Purchasing one increases rate of growth in that area by 25%', Constants.appWidth // 2, 95, size = 13)

def drawItems(app):
    for pot in app.shopItems:
        pot.draw(app.inventory)

def drawHomeButton(app):
    app.goHomeShop.draw()

### MINIGAME

def drawMinigame(app):
    if app.activeMinigame != None:
        app.activeMinigame.draw(app)
        
        hygieneDebuff = int(max(0, 65-app.character.hygieneLevel)) #the lower the level, the higher the opacity
        hygieneDebuff = max(0, hygieneDebuff) #ensure it doesn't fall below 0 and cause error
        drawRect(Constants.appWidth // 2, Constants.appHeight // 2, Constants.appWidth, Constants.appHeight, align = 'center', opacity = hygieneDebuff, fill = 'chartreuse')
        
        
def drawScore(app):
    drawImage('cmu://1166263/46516282/score_info.png', Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')
    if app.activeMinigame != None:
        drawLabel(f'Final Score: {app.activeMinigame.score}', Constants.appWidth // 2, 180)
        drawLabel(f'Coins Earned: {app.activeMinigame.score // 4}', Constants.appWidth // 2, Constants.appHeight // 2) #update later
    app.goHomeScore.draw()
    
def drawFinalScore(app):
    drawImage('cmu://1166263/46516282/score_info.png', Constants.appWidth // 2, Constants.appHeight // 2, align = 'center')
    
    if app.activeMinigame != None:
        drawLabel(f'Final Score: {app.activeMinigame.score}', Constants.appWidth // 2, 180)
        drawLabel(f'High Score: {app.highScore}', Constants.appWidth // 2, Constants.appHeight // 2) #update later
        if app.newHigh:
            drawLabel('New High Score!', Constants.appWidth // 2, Constants.appHeight // 2 + 20, fill = 'red')
    app.goHomeScore.draw()
    
        
##### CONTROLLERS
        
def onStep(app):
    if app.gameOver:
        pass
    if app.activeMinigame and app.activeMinigame.active:
        app.activeMinigame.onStep(app) #just do what should happen in the minigame
    elif app.scene == 'home':
        app.character.move(Constants.homeGroundY)
        
    app.hygiene.level = max(0, min(100, app.hygiene.level))
    app.grooming.level = max(0, min(100, app.grooming.level))
    app.room.level = max(0, min(100, app.room.level))

def onMousePress(app, mouseX, mouseY):
    print('Mouse pressed at: ', mouseX, mouseY)
    if app.inGame:
        pass
    else:
        if app.scene == 'information':
            if app.infoScene == 'title':
                if app.startHomeButton.isClicked(mouseX, mouseY):
                    app.scene = 'home'
            else:
                if app.startGameButton.isClicked(mouseX, mouseY):
                    app.activeMinigame.start(app)
                    app.scene = 'minigame'
                    
        
        if app.scene == 'home':
            for button in app.homeButtons:    
                if button.isClicked(mouseX, mouseY):
                    if button.text == 'Shop':    
                        app.scene = 'shop'
                    elif button.text == 'CLIMB':
                        app.activeMinigame = app.climbGame
                        app.scene = 'information'
                        app.infoScene = 'climb'
                    elif button.text == 'Improve Hygiene':
                        app.activeMinigame = app.hygieneGame
                        app.scene = 'information'
                        app.infoScene = 'hygiene'
                    elif button.text == 'Improve Grooming':
                        app.activeMinigame = app.groomingGame
                        app.scene = 'information'
                        app.infoScene = 'grooming'
                    elif button.text == 'Improve Room':
                        app.activeMinigame = app.roomGame
                        app.scene = 'information'
                        app.infoScene = 'room'
        elif app.scene == 'shop':
            if app.goHomeShop.isClicked(mouseX, mouseY):
                app.scene = 'home'
            for pot in app.shopItems:
                if pot.isClicked(mouseX, mouseY):
                    posInv, posCoins = pot.purchase(app.inventory, app.coins)
                    if (posInv, posCoins) != (None, None):
                        app.inventory, app.coins = posInv, posCoins
                    print(app.inventory)
        elif app.scene == 'minigame':
            if app.activeMinigame and app.activeMinigame.active:
                app.activeMinigame.onMousePress(app, mouseX, mouseY)
        elif app.scene == 'score' or app.scene == 'finalScore':
            if app.goHomeScore.isClicked(mouseX, mouseY):
                app.scene = 'home'

def onMouseDrag(app, mouseX, mouseY):
    if app.scene == 'minigame' and app.activeMinigame == app.roomGame:
        app.activeMinigame.onMouseDrag(app, mouseX, mouseY)
        
def onMouseRelease(app, mouseX, mouseY):
    if app.scene == 'minigame' and app.activeMinigame == app.roomGame:
        app.activeMinigame.onMouseRelease(app, mouseX, mouseY)

def onKeyHold(app, keys):

    if app.scene == 'home' or app.scene == 'minigame':
        if ('left' in keys and 'right' not in keys) or ('a' in keys and 'd' not in keys):
            app.character.vx = -app.character.speed
        elif ('right' in keys and 'left' not in keys) or ('d' in keys and 'a' not in keys):
            app.character.vx = app.character.speed
        else:
            app.character.vx = 0
        if app.character.onGround and ('up' in keys or 'space' in keys or 'w' in keys):
            groomDebuff = max(0, (100 - app.grooming.level) / 20)
            app.character.vy = -13 + groomDebuff  
            app.character.onGround = False
            
            
def onKeyRelease(app, key):
    if key == 'left' or key == 'right' or key == 'a' or key == 'd':
        app.character.vx = 0

def onKeyPress(app, key):
    print('key pressed: ', key)
    if key == 'o':
        app.demoMode = False
        app.devMode = not app.devMode
        print('dev mode = ', app.devMode)
        
    if key == 'p':
        app.devMode = False
        app.demoMode = not app.demoMode
        print('demo mode = ', app.demoMode)
        if app.demoMode:
            app.hygiene.level = 50
            app.coins = 30
            app.grooming.level = 50
            app.room.level = 50
            
    if key == '[':
        app.devMode = False
        app.OPMode = not app.OPMode
        print('OP mode = ', app.OPMode)
        if app.OPMode:
            app.hygiene.level = 100
            app.coins = 300
            app.grooming.level = 100
            app.room.level = 100
    
    if not app.devMode:
        app.minigameLength = 15
        
    if app.devMode:
        app.minigameLength = 4
        if key == 'h':
            app.hygiene.level += 15
        elif key == 'g':
            app.grooming.level += 15
        elif key == 'r':
            app.room.level += 15
        elif key == 'c':
            app.coins += 15
        elif key == 'p':
            app.scene = 'home'
    
def main():
    runApp()

main()
