# Jhonny walker 
# version = 0.1


import time

from System.Collections.Generic import List
from System import Byte, Int32




### NEW walkTo
#  from lib.move import walkTo
def walkDirection(x,y):
    dx = x - Player.Position.X
    dy = y - Player.Position.Y
    dir = "None"
    if dx < 0 and dy == 0: dir = "West"
    if dx == 0 and dy < 0: dir = "North"
    if dx < 0 and dy < 0: dir = "Up"
    
    if dx > 0 and dy == 0: dir = "East"
    if dx == 0 and dy > 0: dir = "South"
    if dx > 0 and dy > 0: dir = "Down"
        
    if dx < 0 and dy > 0: dir = "Left"
    if dx > 0 and dy < 0: dir = "Right"
    #Misc.SendMessage("{} {}".format(Player.Position.X, Player.Position.Y))
    #Misc.SendMessage("Direction {}".format(dir))
    return dir
    
#    
def walkTo(x,y,z=Player.Position.Z, tollerance=1, run=True, timeout=10, pathfinding=False, precise=True):
    maxtime = time.time()+timeout
    dist = distance(Player.Position.X,Player.Position.Y,x,y)
    
    dt = 0.1
    last_positon = Player.Position
    speed_check = time.time()+dt
    next_pathfind = time.time()
    speed = 0
    walk = True
    while walk:
        dist = distance(Player.Position.X,Player.Position.Y,x,y)
        
        if dist <= tollerance:
            #Misc.SendMessage("Arrivd",40)
            walk = False
            break
        
        if not pathfinding or dist > 15:
            #Misc.SendMessage("Walk",40)
            dir = walkDirection(x,y)
            if dir != "None": Player.Run(dir)
        elif speed < 2 and time.time()>next_pathfind:
            #Misc.SendMessage("PF!",30)
            Player.PathFindTo(x,y,z)
            next_pathfind = time.time()+1
        
        if time.time()>speed_check:
            d = distance(Player.Position.X,Player.Position.Y,last_positon.X,last_positon.Y)
            speed = ((d/dt)+speed) / 2
            #Misc.SendMessage("TPS: %.1f"%(speed))
            last_positon = Player.Position
            speed_check = time.time()+dt
        
        if time.time() > maxtime:
            #Misc.SendMessage("timout",40)
            walk = False
            break
    #
        
        
    dist = distance(Player.Position.X,Player.Position.Y,x,y)
    expired = maxtime < time.time()
    return dist, expired


def distance(x1,y1,x2,y2):
    return max(abs(x1-x2),abs(y1-y2))



# stange player body type: 0x00B8

def main():

    
    here = (2227, 1172)
    
    trinsic_forest_dst = (1521, 2679)
    trinsic_mage_dst = (1847, 2711)
    nujelm_bank_dst = (3762, 1304)
    brit_bridge_dst = (1374, 1750)
    recinto_casa = (1124,3570)
    bridge_trin_brit = (1480,2168)
    
    maze_brit_0 = (1481,1578)
    maze_brit_1 = (1600,1656)
    
    dst = here
    
    starttime = time.time()
    dist, success = PathFinder.go(dst, timeout=100,searchTimeout=10)
    if success:
        Player.HeadMessage(68,"Arrived!")
    else:
        Player.HeadMessage(38,"Not Arrived!")
    dt = time.time() - starttime
    Misc.SendMessage("DT: {}s | ".format(dt),20)
    
    
    
    ###
    1/0
    repeat = 1
    
    dist = max(abs(src[0]-dst[0]),abs(src[1]-dst[1]))
    pf = PathFinder( dst )
    sum_dt = 0
    for i in xrange(repeat):
        starttime = time.time()
        
        foundPath = pf.searchPath()
        #pf.exportGrid()
        path, arrived = pf.getWaypoints()
        
        endtime = time.time()
        dt = endtime - starttime
        #Misc.SendMessage("DT: {}s | ".format(dt),20)
        sum_dt += dt
        
        if not foundPath: 
            Player.HeadMessage(40,"NO PATH!!!")
            break
        
        if not arrived: 
            Player.HeadMessage(50,"INCOMPLETE")
            break
        
        
    steps = len(path)
    Misc.SendMessage("DIST: {} | STEPS: {} ".format(dist, steps),20)
    Misc.SendMessage("AVG DT: {}s | ".format(sum_dt/repeat),20)
    
    for x,y in path:
        dist,expired = walkTo(x,y,tollerance=0,timeout=1)
        
            #Misc.Pause(1000)


class PathFinder():
    Unexplored = -1
    NoWalk = -2
    Occupied = -3
    OutOfBound = -4    
    
    
    @staticmethod
    def go(dst, src=None, max_dist=None, avoid_mobs=True, timeout=None, searchTimeout=None):
        if timeout is None: timeout = 0.4
        if src is None: src = (Player.Position.X,Player.Position.Y)
        pf = PathFinder( dst )
        endtime = time.time()+timeout
        dist = max(abs(src[0]-dst[0]),abs(src[1]-dst[1]))
        while time.time() < endtime:
            foundPath = pf.searchPath( max_dist, avoid_mobs, timeout = searchTimeout )
            if not foundPath: 
                Player.HeadMessage(38,"Cannot find path to {} which is {} tiles away.".format(dst,dist))
                return dist, False
            #
            #tile=pf.map.getTile(1373, 1943)
            #Misc.SendMessage("tILE  HOUSE: {}".format(pf.isTileOccupied(tile)),50)
            #
            path, arrived = pf.getWaypoints()
            if not arrived: 
                Player.HeadMessage(38,"Path is incomplete, {} tiles for {} distance.".format(len(path),dist))
                return dist, False
            
            for x,y in path:
                dist,expired = walkTo(x,y,tollerance=0,timeout=1)
                if dist>0 and expired: 
                    break
        #
        return dist, time.time() > endtime
    
    
    def __init__(self, dst, src=None, max_range=18):
        if src is None: src = (Player.Position.X,Player.Position.Y)
        
        self.width = abs(src[0]-dst[0]) # self.max_x-self.min_x 
        self.height =  abs(src[1]-dst[1]) #self.max_y-self.min_y
        
        self.grid = {}
        
        self.map = TileMap() 
        
        self.src_tile = self.map.getTile(src[0],src[1])
        self.dst_tile = self.map.getTile(dst[0],dst[1])      
      
        self.mobMap = {}
        self.mobMapUpdate = 0
        
        self.itemMap = {}
        self.itemMapUpdate = 0        
    #
    
    def clearValues(self):
        self.grid = {}
        
    def getValue(self,tile):
        tile_key = tile.key()
        if tile_key in self.grid: return self.grid[tile_key] 
        return PathFinder.Unexplored
        
    def setValue(self,tile,value):
        tile_key = tile.key()
        self.grid[tile_key] = value
    #   
    def bounds(self):
        path = [self.src_tile.coords(), self.dst_tile.coords()]
        min_x = max_x = path[0][0]
        min_y = max_y = path[0][1]
        for x,y in path:
            if x > max_x: max_x = x
            if y > max_y: max_y = y
            if x < min_x: min_x = x
            if y < min_y: min_y = y
        
        return [min_x, min_y, max_x, max_y]
   
    
    def exportGrid(self, filename = None, border=None):
        if filename is None: filename = './data/jhonny_walker_export.csv'
        if border is None: border = 5
            
        rect = self.bounds()
        
        top_left = rect[0]-border, rect[1]-border
        bot_right = rect[2]+border, rect[3]+border
        Misc.SendMessage("rect: {}".format(rect),20)
        wx, hy = bot_right[0]-top_left[0], bot_right[1]-top_left[1]
        Misc.SendMessage("W,H: {},{}".format(wx,hy),20)
        
        offset_x = top_left[0]
        offset_y = top_left[1]
        
        
        path, arrived = self.getWaypoints()
        csvData = [ ['_'] * (hy+1) for i in xrange(wx+1)]
        for y in xrange(wx):
            for x in xrange(hy):
                key = (x+offset_x,y+offset_y)
                if key in self.grid:
                    csvData[x][y] = self.grid[key] 
                if key in path:
                    csvData[x][y] *= 1000
        #
        src_t = self.src_tile
        src_x, src_y =  src_t.x-offset_x, src_t.y-offset_y
        csvData[src_x][src_y] = 'SRC'
        
        dst_t = self.dst_tile
        dst_x,dst_y =  dst_t.x-offset_x, dst_t.y-offset_y
        csvData[dst_x][dst_y] = 'DST'
        
        saveCSV(filename,csvData)
    #
    def searchPath(self, max_dist=None, avoid_mobs=True, timeout=None): 
        if timeout is None: timeout = 1
        if max_dist is None: max_dist = max(100,max(self.width,self.height) * 2)
        #Misc.SendMessage("max_dist: {}".format(max_dist),20)
        self.clearValues()
        
        lastDist = max_dist
        
        startsearch = time.time()
        
        self.dst_tile.bestTileFor(Player.Position.Z, remember=True)
        queue = [self.dst_tile]
        
        endtime = time.time()+timeout
        self.setValue(self.dst_tile,0)
        while True:
            # finisco le celle prima di trovare la destinazione
            if len(queue) == 0: return False
                
            if time.time()>endtime: return False
            #
            # POP Closest 
            queue = sorted(queue,key = lambda x: x.distance(self.src_tile), reverse=True )
            
            cur_tile = queue.pop(-1)
            
            #cur_key = cur_tile.key()
            cur_val = self.getValue(cur_tile) #grid[cur_key]    
            #cur_z = cur_tile.bestTile.z
            
            cur_dist = cur_tile.distance(self.src_tile)
            if cur_dist != lastDist:
                lastDist = cur_dist
                #Misc.SendMessage("Distance: {}, steps: {} ".format(cur_dist, cur_val),20)
            
            if cur_tile == self.src_tile: 
                Misc.SendMessage("Destination is {} step away!!!".format(cur_val),20)
                break
            
            #pop nearby
            near_tiles = self.map.tilesNear(cur_tile)
            for next_tile in near_tiles:
                next_val = self.getValue(next_tile) #grid[k]
                
                to_skip = [ PathFinder.NoWalk, PathFinder.OutOfBound, PathFinder.Occupied ]
                if next_val in to_skip: continue
                #
                #if not self.coordsValid(tile.x,tile.y): 
                if next_tile.distance(self.src_tile) > max_dist:
                    self.setValue(next_tile,PathFinder.OutOfBound)
                    #Misc.SendMessage("Too far!")
                    continue
                
                
                if not next_tile.canWalk(cur_tile.bestTile.z):
                    #Misc.SendMessage("NO WALK")
                    if self.getValue(next_tile)<0:
                        self.setValue(next_tile,PathFinder.NoWalk)
                    #
                    continue
                    
                if avoid_mobs and self.isTileOccupied(next_tile) and next_tile != self.src_tile:
                    self.setValue(next_tile,PathFinder.Occupied)
                    continue
                
                if next_val == PathFinder.Unexplored or next_val > cur_val+1:
                    self.setValue(next_tile,cur_val+1)
                    next_tile.bestTile = next_tile.bestTileFor(cur_tile.bestTile.z,remember=True)
                    if next_val == PathFinder.Unexplored:
                    
                        queue.append( next_tile )
                #    
            #
        #
        return True
        
    
    def getWaypoints(self):
        if len(self.grid)==0: return [], False
        if self.src_tile == self.dst_tile: return [],True
            
        path = []
        cur_tile = self.src_tile
        arrived = True
        while cur_tile != self.dst_tile: # not in self.map.tilesNear(self.dst_tile):
            path.append( cur_tile.coords() )
            
            #if len(path) % 10 == 0:
            #    Misc.SendMessage("path len {}".format(len(path)),100) 
            #    Misc.Pause(50)
            
            cur_val = self.getValue(cur_tile)
            #Misc.SendMessage("cur_val:{}".format(cur_val),100) 
            
            
            near_tiles = self.map.tilesNear(cur_tile)
            new_tile = None
            for next_tile in near_tiles:
                next_val = self.getValue(next_tile)
                
                if next_val < 0: 
                    #Misc.SendMessage("NEGATIVE :{}".format(next_val),100) 
                    continue
                
                if next_val < cur_val:
                    new_tile = next_tile
                #
            #
            if new_tile is None: 
                arrived = False
                break
            cur_tile = new_tile
        #            
        path.append(cur_tile.coords())
        
        Misc.SendMessage("path len {}".format(len(path)),100) 
        
        #Misc.SendMessage("search {} | compose: {}".format( (stime*100)//dt,(ctime*100)//dt ) ,100 )
        return path, arrived
    
    
    def isTileOccupied(self,tile,avoidHouse=True,avoidMobs=True):    
        if not self.inPlayerRange(tile): return False
            
        if avoidHouse and self.isHouseTile(tile): return True
        if avoidMobs and self.isMobInTile(tile): return True
        if self.isItemInTile(tile): return True
            
        return False
        
    def inPlayerRange(self,tile):
        dist = max(abs(tile.x-Player.Position.X), abs(tile.y-Player.Position.Y))
        return dist < 18
        
    def isHouseTile(self,tile):
        if not self.inPlayerRange(tile): return False
        isHouse = Statics.CheckDeedHouse(tile.x,tile.y)
        #if isHouse:
            #Misc.SendMessage("House {}".format(isHouse),100) 
            #Misc.Pause(100)
        return isHouse
    
    def isItemInTile(self,tile):
        if not self.inPlayerRange(tile): return False
        impassableItems = [0x0B24,0x0C8F,0x2FF6]
            
        if time.time()>self.itemMapUpdate:
            self.itemMapUpdate = time.time()+2
            options = Items.Filter()
            options.OnGround = True
            options.Graphics = List[Int32](impassableItems)
            all = Items.ApplyFilter(options)
            self.itemMap = {(m.Position.X,m.Position.Y):m for m in all}
        #
        return (tile.x,tile.y) in self.itemMap
        
    def isMobInTile(self,tile):
        if not self.inPlayerRange(tile): return False
        
        if time.time()>self.mobMapUpdate:
            self.mobMapUpdate = time.time()+0.3
            all = Mobiles.ApplyFilter(Mobiles.Filter())
            self.mobMap = {(m.Position.X,m.Position.Y):m for m in all}
        #
        return (tile.x,tile.y) in self.mobMap
    
    

class TileMap():
    def __init__(self): #,rect):
        self.tiles = {}
        #self.rect = rect
        #self.min_x = rect[0]
        #self.min_y = rect[1]
        #self.max_x = rect[2]
        #self.max_y = rect[3]
    
    def getTile(self, x,y,z=None, autoload=True):
        if (x,y) in self.tiles:
            if z is not None:
                self.tiles[(x,y)].bestTileFor(z,remember=True)
            return self.tiles[(x,y)]
        elif autoload:
            self.tiles[(x,y)] = TileStack(x,y,z)
            return self.tiles[(x,y)]
        return None
    
    def tilesNear(self,tile):
        return [
            # X
            self.getTile(tile.x+1,tile.y+1),
            self.getTile(tile.x-1,tile.y-1),
            self.getTile(tile.x+1,tile.y-1),
            self.getTile(tile.x-1,tile.y+1),
            
            # +
            self.getTile(tile.x+1,tile.y),
            self.getTile(tile.x-1,tile.y),
            self.getTile(tile.x,tile.y+1),
            self.getTile(tile.x,tile.y-1),
            
            
        ]
        
        
    
class TileStack():
    def __init__(self,x,y,z=None):
        self.x = x
        self.y = y

        self.stack = []
        
        self.read()
        self.bestTile = None 
        
        if z is None: 
            z = Player.Position.Z
        
        self.bestTileFor(z,remember=True)
    
    def key(self):
        #return "{}_{}".format(*self.coords())
        return self.coords()
        
    def __hash__(self):
        return hash(self.key())
            
    def read(self):
        x,y = self.x,self.y
        z = Statics.GetLandZ(x,y,Player.Map)
        staticID = Statics.GetLandID(x,y,Player.Map)
        t = Tile(Tile.Land, x, y, z, staticID)
        if not t.toDiscard():
            self.stack.append(t)
        #
        for tileinfo in Statics.GetStaticsTileInfo(x,y,Player.Map):
            t = Tile(Tile.Tile, x, y, tileinfo.StaticZ, tileinfo.StaticID)
            if not t.toDiscard():
                self.stack.append(t)
            #
        #
        return True
    #v
    def bestTileFor(self,z=None,remember=False):
        if z is None: z = Player.Position.Z
        if len(self.stack) == 0: return None
        
        #walkable
        #walkable = filter(lambda x: x.canWalk(), self.stack)
        #if len(walkable) == 0: 
            #Misc.SendMessage("bestTileFor {} -> {}".format(z,self.bestTile.name),200)
            #walkable = 
        
        #closest
        zNear = list(sorted(self.stack, key=lambda x: abs(x.z-z)))
        best = zNear[0]
        
        #positive
        #equals = filter(lambda x: abs(x.z) == abs(best.z), self.stack )
        #highers = sorted(equals , key = lambda x: x.z, reverse=True)
        #best = equals[0]
        
        above = self.inRange(best.z)
        walkable = list(filter(lambda x: x.canWalk(), above))
        if len(walkable)>0: best = walkable[-1]
            
        if remember: self.bestTile = best
        #
        #if not self.canWalk(best.z):
            #Misc.SendMessage("NO WALK: {}".format(self.bestTile.name),200)
            #Misc.Pause(100)
        return best
    #
    def inRange(self,z,zDelta=19):
        return sorted(filter(lambda x: z-3 <= x.z <= z+zDelta, self.stack), key=lambda x: x.z)
    #        
    def coords(self):
        return (self.x,self.y)
    #        
    def __eq__(self,tile):
        return tile.x == self.x and tile.y == self.y
    #        
    def canWalk(self,z=None):
        if z is None: z = Player.Position.Z
        closest = self.bestTileFor(z)
        #Misc.SendMessage("W: {}".format(closest.z),20)
        if closest is None: 
            return None
        
        tiles = self.inRange(closest.z)
        if len(tiles)==0: return False
        #Misc.SendMessage("W: {}".format(len(tiles)),20)
        #
        blocking = list(filter(lambda x: not x.canWalk(), tiles))
        walkable = (len(blocking)==0)
        if walkable:
            self.bestTileFor(tiles[-1].z,remember=True)
        return walkable
    #    
    def distance(self, tile, euclid=False):
        if euclid:
            return ((self.x-tile.x)**2 + (self.y-tile.y)**2)**0.5
        else:
            return max(abs(self.x-tile.x),abs(self.y-tile.y))
            
    def __repr__(self):
        return self.__str__()
            
    def __str__(self):
        coords = (self.x, self.y)
        walk = 'yes' if self.canWalk() else 'NO!'
        return "TILE{}: {}, WALK: {} ".format(coords,self.bestTileFor().name,walk)
            
class Tile():
    Land = 'Land'
    Tile = 'Tile'
    
    Impassable = 'Impassable'
    Wall = 'Wall'
    Wet = 'Wet'
    Surface = 'Surface'
    NoFlag = 'None'
    
    
    def __init__(self, kind, x, y, z, staticID):
        self.x = x
        self.y = y
        self.z = z
        
        self.kind = kind
        self.staticID = staticID
        self.name = "-NOT-FOUND-"
        
        #flags
        self.impassable = False
        self.wall = False
        self.wet = False
        self.surface = False
        self.noFlag = False
        
        
        if kind == Tile.Tile:
            self.name = Statics.GetTileName(self.staticID)
            self.impassable = Statics.GetTileFlag(self.staticID,Tile.Impassable)
            self.wall = Statics.GetTileFlag(self.staticID,Tile.Wall)
            self.wet = Statics.GetTileFlag(self.staticID,Tile.Wet)
            self.surface = Statics.GetTileFlag(self.staticID,Tile.Surface)
            self.noFlag = Statics.GetTileFlag(self.staticID,Tile.NoFlag)
        elif kind == Tile.Land:
            self.name = Statics.GetLandName(self.staticID)
            self.impassable = Statics.GetLandFlag(self.staticID,Tile.Impassable)
            self.wall = Statics.GetLandFlag(self.staticID,Tile.Wall)
            self.wet = Statics.GetLandFlag(self.staticID,Tile.Wet)
            self.surface = Statics.GetLandFlag(self.staticID,Tile.Surface)
            self.noFlag = Statics.GetLandFlag(self.staticID,Tile.NoFlag)
    
    def toDiscard(self):
        discard = not (self.impassable or self.wall or self.wet or self.surface or self.noFlag)
        #if discard:
            #Misc.SendMessage("DISCARD: {}".format(self.name),38)
        return discard
            
    def canWalk(self):
        return not(self.impassable) and not(self.wall) and not(self.wet) #not(self.impassable or self.wall or self.wet)

    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        coords = (self.x, self.y, self.z)
        walk = 'yes' if self.canWalk() else 'NO!'
        return "Tile.{}{}: {}, WALK: {} ".format(self.kind, coords, self.name, walk) 
    
                
if __name__ == '__main__':
    main()
            
        