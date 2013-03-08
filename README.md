# LiveStats - Online Statistical Algorithms for Python

LiveStats solves the problem of generating accurate statistics for when your data set is too large to fit in memory, or too costly to sort. Just add your data to the LiveStats object, and query the methods on it to produce statistical estimates of your data.

LiveStats doesn't keep any items in memory, only estimates of the statistics. This means you can calculate statistics on an arbitrary amount of data.

## Example usage

When constructing a LiveStats object, pass in an array of the quantiles you wish you track. LiveStats stores 15 double values per quantile supplied.

    from livestats import LiveStats
    from math import sqrt
    import random

    test = LiveStats([0.25, 0.5, 0.75])

    data = iter(random.random, 1)

    for x in xrange(3):
        for y in xrange(100):
            test.add(data.next()*100)

        print "Average {}, stddev {}, quantiles {}".format(test.mean(), 
                sqrt(test.variance()), test.quantiles())

Easy.

## How accurate is it?

Very accurate. If you run livestats.py as a script with a numeric argument, it'll run some tests with that many data points. As soon as you start to get over 10,000 elements, accuracy to the actual quantiles is well below 1%. At 10,000,000, it's this:

    Uniform:    Avg%E 1.732260e-12 Var%E 2.999999e-05 Quant%E 1.315983e-05
    Expovar:    Avg%E 9.999994e-06 Var%E 1.000523e-05 Quant%E 1.741774e-05
    Triangular: Avg%E 9.988727e-06 Var%E 4.839340e-12 Quant%E 0.015595
    Bimodal:    Avg%E 9.999991e-06 Var%E 4.555303e-05 Quant%E 9.047849e-06

That's percent error for the cumulative moving average, variance, and the average percent error for four different random distributions at three quantiules, 25th, 50th, and 75th. Pretty good.

# More details

LiveStats uses the [P-Square Algorithm for Dynamic Calculation of Quantiles and Histograms without Storing Observations](http://www.cs.wustl.edu/~jain/papers/ftp/psqr.pdf) and other online statistical algorithms. I also [wrote a post](http://blog.existentialize.com/on-accepting-interview-question-answers.html) on where I got this idea.

