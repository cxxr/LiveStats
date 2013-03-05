#!/usr/bin/env python

from array import array
from math import fabs,copysign
import random, sys

def calcP2(q, qm1, d, np1, n, nm1):
    outer = d / ( np1 - nm1 )
    inner_left = ( n - nm1 + d ) * ( qp1 - q ) / ( np1 - n )
    inner_right = ( np1 - n - d ) * ( q - qm1 ) / ( n - nm1 )

    return q + outer * ( inner_left + inner_right)

class LiveHistogram:
    heights = []
    initialized = False

    def __init__(self, num_cells = 10):
        self.num_cells = num_cells + 1
        self.pos = list(range(num_cells))

    def add(self, item):
        if len(self.heights) < self.num_cells + 1:
            self.heights.append(item)
        else:
            if self.initialized == False:
                self.heights.sort
                self.initialized = True

            # find cell k
            if self.heights[0] > item:
                self.heights[0] = item
                k = 0
            else:
                for i in range(1, len(self.heights) - 1):
                    if self.heights[i] < item and item < self.heights[i + 1]:
                        k = i
                        break
                else:
                    k = self.num_cells - 1
                    if self.heights[-1] < item:
                        self.heights[-1] = item

            # increment all positions greater than k
            self.pos = self.pos[:k] + [x + 1 for x in self.pos[k:]]
            self.__adjust

    def __adjust(self):
        for i in range(1, self.num_cells - 1):
            n = self.pos[i]
            q = self.heights[i]
            nn = 1.0 + (i - 1.0)*(n - 1.0)/(self.num_cells - 1.0)
            dist = nn - n
            back_dist = self.pos[i - 1] - n
            forw_dist = self.pos[i + 1] - n

            if (dist >= 1 and forw_dist > 1) or (dist <= -1 and back_dist < -1):
                dist = copysign(1, dist)
                qn = calcP2(q, self.heights[i - 1], dist, self.pos[i + 1], n, self.pos[i - 1])
                if self.heights[i - 1] < qn and qn < self.heights[i + 1]:
                    self.heights[i] = qn
                else:
                    # use linear form
                    self.heights[i] = q + dist * (self.heights[i + dist] - q) / (self.pos[i + dist] - n)

                self.pos[i] = n + dist

    def histogram(self):
        if self.initialized == True:
            # We have enough data to generate the histogram
            return zip(self.pos, self.heights)
        else:
            return []


def bimodal( low1, high1, mode1, low2, high2, mode2 ):
    toss = random.choice( (1, 2) )
    if toss == 1:
        return random.triangular( low1, high1, mode1 )
    else:
        return random.triangular( low2, high2, mode2 )

def output (tuples, name):
    print name + " histogram:"
    for t in tuples:
        print str(t[0]) + ": " + str(t[1])


if __name__ == '__main__':
    count = int(sys.argv[1])
    random.seed()

    median = LiveHistogram(4)
    test = [1, 2, 3, 4, 5, 6, 22.37, 10.15, 15.43]
    for i in test:
        median.add(i)

    output(median.histogram(), "Test")

    median = LiveHistogram()
    x = list(range(count))
    random.shuffle(x)
    for i in x:
        median.add(i)

    output(median.histogram(), "Uniform")

    median = LiveHistogram()
    for i in range(count):
        x[i] = random.expovariate(1.0/435)
        median.add(x[i])

    output(median.histogram(), "Random")

    median = LiveHistogram()
    for i in range(count):
        x[i] = random.triangular(-1000, 1000, 999)
        median.add(x[i])

    output(median.histogram(), "Triangular")

    median = LiveHistogram()
    for i in range(count):
        x[i] = bimodal(0, 1000, 500, 500, 1500, 1400)
        median.add(x[i])

    output(median.histogram(), "Bimodal")



