#!/usr/bin/env python

from math import copysign,fabs,sqrt
import random, sys

def calcP2(qp1, q, qm1, d, np1, n, nm1):
    d = float(d)
    n = float(n)
    np1 = float(np1)
    nm1 = float(nm1)

    outer = d / (np1 - nm1)
    inner_left = (n - nm1 + d) * (qp1 - q ) / (np1 - n)
    inner_right = (np1 - n - d) * (q - qm1 ) / (n - nm1)

    return q + outer * (inner_left + inner_right)

class Percentile:
    LEN = 5
    def __init__(self, p):
        self.dn = [0, p/2, p, (1 + p)/2, 1]
        self.npos = [1, 1 + 2*p, 1 + 4*p, 3 + 2*p, 5]
        self.pos = range(1, self.LEN + 1)
        self.heights = []
        self.initialized = False

    def add(self, item):
        if len(self.heights) != 5:
            self.heights.append(item)
        else:
            if self.initialized == False:
                self.heights.sort()
                self.initialized = True

            # find cell k
            if item < self.heights[0]:
                self.heights[0] = item
                k = 1
            else:
                for i in range(1, self.LEN):
                    if self.heights[i - 1] <= item and item < self.heights[i]:
                        k = i
                        break
                else:
                    k = 4
                    if self.heights[-1] < item:
                        self.heights[-1] = item

            # increment all positions greater than k
            self.pos = self.pos[:k] + [x + 1 for x in self.pos[k:]]
            self.npos = [x + y for x,y in zip(self.npos, self.dn)]

            self.__adjust()

    def __adjust(self):
        for i in range(1, self.LEN - 1):
            n = self.pos[i]
            q = self.heights[i]

            d = self.npos[i] - n

            if (d >= 1 and self.pos[i + 1] - n > 1) or (d <= -1 and self.pos[i - 1] - n < -1):
                d = int(copysign(1,d))

                qp1 = self.heights[i + 1]
                qm1 = self.heights[i - 1]
                np1 = self.pos[i + 1]
                nm1 = self.pos[i - 1]
                qn = calcP2(qp1, q, qm1, d, np1, n, nm1)

                if qm1 < qn and qn < qp1:
                    self.heights[i] = qn
                else:
                    # use linear form
                    self.heights[i] = q + d * (self.heights[i + d] - q) / (self.pos[i + d] - n)

                self.pos[i] = n + d

    def percentile(self):
        if self.initialized:
            return self.heights[2]
        else:
            return 0


class LiveStats:
    def __init__(self, p = [0.5]):
        self.var_m2 = 0.0
        self.average = 0.0
        self.count = 1
        self.tiles = {}
        self.initialized = False
        for i in p:
            self.tiles[i] = Percentile(i)

    def add(self, item):
        delta = item - self.average

        # Average
        self.average = (self.count * self.average + item) / (self.count + 1)
        self.count = self.count + 1

        # Variance (except for the scale)
        self.var_m2 = self.var_m2 + delta * (item - self.average)

        # tiles
        for perc in self.tiles.values():
            perc.add(item)


    def percentiles(self):
        # We have enough data to generate the tiles
        return [x.percentile() for x in self.tiles.values()]

    def mean(self):
        return self.average

    def num(self):
        return self.count

    def variance(self):
        return self.var_m2 / (self.count - 1)


def bimodal( low1, high1, mode1, low2, high2, mode2 ):
    toss = random.choice( (1, 2) )
    if toss == 1:
        return random.triangular( low1, high1, mode1 )
    else:
        return random.triangular( low2, high2, mode2 )

def output (tiles, data, stats, name):
    data.sort()
    tuples = stats.percentiles()
    med = [data[int(len(data) * x)] for x in tiles]
    pe = 0
    for approx, exact in zip(tuples, med):
        pe = pe + (fabs(approx - exact)/fabs(exact))
    pe = 100.0 * pe / len(data)

    print "{0}: Estimated: {1}, Actual: {2}, Avg: {3}, Stddev: {4} %Error {5}".format(name, 
            tuples, med, stats.mean(), sqrt(stats.variance()), pe)


if __name__ == '__main__':
    count = int(sys.argv[1])
    random.seed()

    tiles = [0.25, 0.5, 0.75]

    median = LiveStats(tiles)
    test = [0.02, 0.15, 0.74, 3.39, 0.83, 22.37, 10.15, 15.43, 38.62, 15.92, 34.60,
            10.28, 1.47, 0.40, 0.05, 11.39, 0.27, 0.42, 0.09, 11.37]
    for i in test:
        median.add(i)

    output(tiles, test, median, "Test")

    median = LiveStats(tiles)
    x = range(count)
    random.shuffle(x)
    for i in x:
        median.add(i)

    output(tiles, x, median, "Uniform")

    median = LiveStats(tiles)
    for i in xrange(count):
        x[i] = random.expovariate(1.0/435)
        median.add(x[i])

    output(tiles, x, median, "Random")

    median = LiveStats(tiles)
    for i in xrange(count):
        x[i] = random.triangular(-1000, 1000, 999)
        median.add(x[i])

    output(tiles, x, median, "Triangular")

    median = LiveStats(tiles)
    for i in xrange(count):
        x[i] = bimodal(0, 1000, 500, 500, 1500, 1400)
        median.add(x[i])

    output(tiles, x, median, "Bimodal")



