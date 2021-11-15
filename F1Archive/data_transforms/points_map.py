import numpy as np

class MapPoints():
    """
    methods for mapping between points systems for different F1 seasons.
    Points systems taken from:
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """
    def __init__(self, initial_system):
        
        self._1950 = np.array([8,6,4,3,2])
        self._1960 = np.array([9,6,4,3,2,1])
        self._1991 = np.array([10,6,4,3,2,1])
        self._2003 = np.array([10,8,6,5,4,3,2,1])
        self._2010 = np.array([25,18,15,12,10,8,6,4,2,1])

        self.initial_system = self.get_points(initial_system)


    def to_1990(self):
        
        pass

    def to_2003(self):
        pass

    
    def get_points(self, year):
        
        if not (isinstance(year, int) or isinstance(year,str)):
            return self._2010
        if 1950 <= int(year) <= 1959:
            points = self._1950
        elif 1960 <= int(year) <= 1990:
            points = self._1960
        elif 1991 <= int(year) <= 2002:
            points = self._1991
        elif 2003 <= int(year) <= 2009:
            points = self._2003
        else:
            points = self._2010
            
        return points


if __name__ == '__main__':
    a = np.array([0,0,0,0,0,0,0,0,1,0,0,2,0,0,0,3,0,0,0,4,0,6,0,0,9])
    b = np.array([0,0,0,0,0,0,0,0,1,0,0,2,0,0,0,3,0,0,0,4,0,6,0,0,10])

    c = np.array([0,0,0,0,0,0,0,0,1,0,0,2,0,5,0,3,0,0,0,4,0,6,8,0,10])

    print(sum(set(a)))
    print(sum(set(b)))
    print(sum(set(c)))

    print(np.where(a == 9))

    if sum(set(a)) == 25:
        a[np.where(a == 9)] = 10
        print(a)

    if sum(set(c)) == 39:
        c[np.where(c == 1)] = 0
        c[np.where(c == 2)] = 0
        c[np.where(c == 3)] = 1
        c[np.where(c == 4)] = 2
        c[np.where(c == 5)] = 3
        c[np.where(c == 6)] = 4
        c[np.where(c == 8)] = 6
        print(a)
        print(c)