# LiveStats - Online Statistical Algorithms for Python

LiveStats solves the problem of generating accurate statistics for when your data set is too large to fit in memory, or too costly to sort. Just add your data to the LiveStats object, and query the methods on it to produce statistical estimates of your data.

LiveStats doesn't keep any items in memory, only estimates of the statistics. This means you can calculate statistics on an arbitrary amount of data.

## Example usage

When constructing a LiveStats object, pass in an array of the percentiles you wish you track. LiveStats stores 15 double values per percentile supplied.

    from livestats import LiveStats
    from math import sqrt
    import random

    test = LiveStats([0.25, 0.5, 0.75])

    data = [random.random() * 10 + x for x in range(100)]

    for x in data:
        test.add(x)

    print "Average {}, stddev {}, percentiles {}".format(test.mean(), 
            sqrt(test.variance()), test.percentiles())

Easy.

## How accurate is it?

Very accurate. If you run livestats.py as a script with a numeric argument, it'll run some tests with that many data points. As soon as you start to get over 10,000 elements, accuracy to the actual percentiles is well below 1%. At 10,000,000, it's this:

    Uniform: %Error 1.91823416272e-10
    Random: %Error 1.18853157508e-09
    Triangular: %Error 1.15713743667e-06
    Bimodal: %Error 9.98699912316e-11

That's average percent error for four different random distributions at three percentiles, 25th, 50th, and 75th. Pretty good.   

# More details

LiveStats uses the [P-Square Algorithm for Dynamic Calculation of Quantiles and Histograms without Storing Observations](http://www.cs.wustl.edu/~jain/papers/ftp/psqr.pdf) and other online statistical algorithms.

