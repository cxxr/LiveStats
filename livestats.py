#!/usr/bin/env python

from math import copysign,fabs
import random, sys

def calcP2(qp1, q, qm1, d, np1, n, nm1):
    d = float(d)
    n = float(n)
    np1 = float(np1)
    nm1 = float(nm1)

    outer = d / ( np1 - nm1 )
    inner_left = ( n - nm1 + d ) * ( qp1 - q ) / ( np1 - n )
    inner_right = ( np1 - n - d ) * ( q - qm1 ) / ( n - nm1 )

    #print " {} / ( {} - {} )".format(d, np1, nm1)
    #print "{} + {} * ( {} + {} )".format(q, outer, inner_left, inner_right)

    return q + outer * ( inner_left + inner_right)

class LiveStats:
    def __init__(self, p = [0.5]):
        self.dn = {}
        self.pos = {}
        self.npos = {}
        self.heights = {}
        self.initialized = False
        for i in p:
            self.dn[i] = [0, i/2, i, (1 + i)/2, 1]
            self.npos[i] = [1, 1 + 2*i, 1 + 4*i, 3 + 2*i, 5]
            self.pos[i] = list(range(1, 6))
            self.heights[i] = []


    def add(self, item):
        for key in self.heights.keys():
            if len(self.heights[key]) != 5:
                self.heights[key].append(item)
                return 0
            else:
                if self.initialized == False:
                    self.heights[key].sort()
                    self.initialized = True

                # find cell k
                if item < self.heights[key][0]:
                    self.heights[key][0] = item
                    k = 1
                else:
                    for i in range(1, len(self.heights[key])):
                        if self.heights[key][i - 1] <= item and item < self.heights[key][i]:
                            k = i
                            break
                    else:
                        k = 4
                        if self.heights[key][-1] < item:
                            self.heights[key][-1] = item

                # increment all positions greater than k
                self.pos[key] = self.pos[key][:k] + [x + 1 for x in self.pos[key][k:]]
                self.npos[key] = [x + y for x,y in zip(self.npos[key], self.dn[key])]
                #print "{}\t{}\t{}\t{}".format(item, k, self.pos, self.npos)

                self.__adjust(key)

    def __adjust(self, key):
        for i in range(1, len(self.heights[key]) - 1):
            n = self.pos[key][i]
            q = self.heights[key][i]

            d = self.npos[key][i] - n

            if (d >= 1 and self.pos[key][i + 1] - n > 1) or (d <= -1 and self.pos[key][i - 1] - n < -1):
                d = int(copysign(1,d))

                qp1 = self.heights[key][i + 1]
                qm1 = self.heights[key][i - 1]
                np1 = self.pos[key][i + 1]
                nm1 = self.pos[key][i - 1]
                qn = calcP2(qp1, q, qm1, d, np1, n, nm1)
                #print "{}: {}\n".format(i + 1, qn)

                if qm1 < qn and qn < qp1:
                    self.heights[key][i] = qn
                else:
                    # use linear form
                    self.heights[key][i] = q + d * (self.heights[key][i + d] - q) / (self.pos[key][i + d] - n)

                self.pos[key][i] = n + d
        #print "{}\t{}".format(self.pos, self.heights)


    def percentiles(self):
        if self.initialized == True:
            # We have enough data to generate the percentiles
            return [x[2] for x in self.heights.values()]
        else:
            return []


def bimodal( low1, high1, mode1, low2, high2, mode2 ):
    toss = random.choice( (1, 2) )
    if toss == 1:
        return random.triangular( low1, high1, mode1 )
    else:
        return random.triangular( low2, high2, mode2 )

def output (tiles, data, tuples, name):
    data.sort()
    med = [data[int(len(data) * x)] for x in tiles]
    pe = 0
    for approx, exact in zip(tuples, med):
        pe = pe + (fabs(approx - exact)/fabs(exact))
    pe = 100.0 * pe / len(data)
    avg = sum(data) / len(data)

    print "{0}: Estimated: {1}, Actual: {2}, Avg: {3}, %Error {4}".format(name, tuples, med, avg, pe)


if __name__ == '__main__':
    count = int(sys.argv[1])
    random.seed()

    tiles = [0.25, 0.5, 0.75]

    median = LiveStats(tiles)
    test = [0.02, 0.15, 0.74, 3.39, 0.83, 22.37, 10.15, 15.43, 38.62, 15.92, 34.60,
            10.28, 1.47, 0.40, 0.05, 11.39, 0.27, 0.42, 0.09, 11.37]
    for i in test:
        median.add(i)

    output(tiles, test, median.percentiles(), "Test")

    median = LiveStats(tiles)
    x = list(range(count))
    random.shuffle(x)
    for i in x:
        median.add(i)

    output(tiles, x, median.percentiles(), "Uniform")

    median = LiveStats(tiles)
    for i in range(count):
        x[i] = random.expovariate(1.0/435)
        median.add(x[i])

    output(tiles, x, median.percentiles(), "Random")

    median = LiveStats(tiles)
    for i in range(count):
        x[i] = random.triangular(-1000, 1000, 999)
        median.add(x[i])

    output(tiles, x, median.percentiles(), "Triangular")

    median = LiveStats(tiles)
    for i in range(count):
        x[i] = bimodal(0, 1000, 500, 500, 1500, 1400)
        median.add(x[i])

    output(tiles, x, median.percentiles(), "Bimodal")



