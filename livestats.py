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

class Quantile:
    LEN = 5
    def __init__(self, p):
        """ Constructs a single quantile object """
        self.dn = [0, p/2, p, (1 + p)/2, 1]
        self.npos = [1, 1 + 2*p, 1 + 4*p, 3 + 2*p, 5]
        self.pos = list(range(1, self.LEN + 1))
        self.heights = []
        self.initialized = False
        self.p = p

    def add(self, item):
        """ Adds another datum """
        if len(self.heights) != self.LEN:
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
            self.pos = [j if i < k else j + 1 for i,j in enumerate(self.pos)]
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

    def quantile(self):
        if self.initialized:
            return self.heights[2]
        else:
            self.heights.sort()
            l = len(self.heights)
            # make sure we don't overflow on p == 1 or underflow on p == 0
            return self.heights[int(min(max(l - 1, 0), l * self.p))]


class LiveStats:
    def __init__(self, p = [0.5]):
        """ Constructs a LiveStream object

        Keyword arguments:

        p -- A list of quantiles to track, by default, [0.5]

        """
        self.min_val = float('inf')
        self.max_val = float('-inf')
        self.var_m2 = 0.0
        self.kurt_m4 = 0.0
        self.skew_m3 = 0.0
        self.average = 0.0
        self.count = 0
        self.tiles = {}
        self.initialized = False
        for i in p:
            self.tiles[i] = Quantile(i)

    def add(self, item):
        """ Adds another datum """
        delta = item - self.average

        self.min_val = min(self.min_val, item)
        self.max_val = max(self.max_val, item)

        # Average
        self.average = (self.count * self.average + item) / (self.count + 1)
        self.count = self.count + 1

        # Variance (except for the scale)
        self.var_m2 = self.var_m2 + delta * (item - self.average)

        # tiles
        for perc in list(self.tiles.values()):
            perc.add(item)

        # Kurtosis
        self.kurt_m4 = self.kurt_m4 + (item - self.average)**4.0

        # Skewness
        self.skew_m3 = self.skew_m3 + (item - self.average)**3.0


    def quantiles(self):
        """ Returns a list of tuples of the quantile and its location """
        return [(key, val.quantile()) for key, val in self.tiles.items()]

    def maximum(self):
        """ Returns the maximum value given """
        return self.max_val

    def mean(self):
        """ Returns the cumulative moving average of the data """
        return self.average

    def minimum(self):
        """ Returns the minimum value given """
        return self.min_val

    def num(self):
        """ Returns the number of items added so far"""
        return self.count

    def variance(self):
        """ Returns the sample variance of the data given so far"""
        if self.count > 1:
            return self.var_m2 / (self.count - 1)
        else:
            return float('NaN')

    def kurtosis(self):
        """ Returns the sample kurtosis of the data given so far"""
        if self.count > 1:
            return self.kurt_m4 / (self.count * self.variance()**2.0) - 3.0
        else:
            return float('NaN')

    def skewness(self):
        """ Returns the sample skewness of the data given so far"""
        if self.count > 1:
            return self.skew_m3 / (self.count * self.variance()**1.5)
        else:
            return float('NaN')


def bimodal( low1, high1, mode1, low2, high2, mode2 ):
    toss = random.choice( (1, 2) )
    if toss == 1:
        return random.triangular( low1, high1, mode1 )
    else:
        return random.triangular( low2, high2, mode2 )

def output (tiles, data, stats, name):
    data.sort()
    tuples = [x[1] for x in stats.quantiles()]
    med = [data[int(len(data) * x)] for x in tiles]
    pe = 0
    for approx, exact in zip(tuples, med):
        pe = pe + (fabs(approx - exact)/fabs(exact))
    pe = 100.0 * pe / len(data)
    avg = sum(data)/len(data)

    s2 = 0
    for x in data:
        s2 = s2 + (x - avg)**2
    var = s2 / len(data)

    v_pe = 100.0*fabs(stats.variance() - var)/fabs(var)
    avg_pe = 100.0*fabs(stats.mean() - avg)/fabs(avg)

    print("{}: Avg%E {} Var%E {} Quant%E {}, Kurtosis {}, Skewness {}".format(
            name, avg_pe, v_pe, pe, stats.kurtosis(), stats.skewness()));


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
    x = list(range(count))
    random.shuffle(x)
    for i in x:
        median.add(i)

    output(tiles, x, median, "Uniform")

    median = LiveStats(tiles)
    for i in range(count):
        x[i] = random.expovariate(1.0/435)
        median.add(x[i])

    output(tiles, x, median, "Expovar")

    median = LiveStats(tiles)
    for i in range(count):
        x[i] = random.triangular(-1000*count/10, 1000*count/10, 100)
        median.add(x[i])

    output(tiles, x, median, "Triangular")

    median = LiveStats(tiles)
    for i in range(count):
        x[i] = bimodal(0, 1000, 500, 500, 1500, 1400)
        median.add(x[i])

    output(tiles, x, median, "Bimodal")



