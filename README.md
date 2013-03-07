# LiveStats - Online Statistical Algorithms for Python

LiveStats solves the problem of generating accurate statistics for when your data set is too large to fit in memory, or too costly to sort. Just add your data to the LiveStats object, and query the methods on it to produce statistical estimates of your data.

LiveStats doesn't keep any items in memory, only estimates of the statistics. This means you can calculate statistics on an arbitrary amount of data.

## Example usage

When constructing a LiveStats object, pass in an array of the percentiles you wish you track. LiveStats stores 15 double values per percentile supplied.

    from livestats import LiveStats
    from math import sqrt

    test = LiveStats([0.25, 0.5, 0.75])

    for x in data:
        test.add(x)

    print "Average {}, stddev {}, percentiles {}".format(test.mean(), 
            sqrt(test.variance()), test.percentiles())

Easy.

# More details

LiveStats uses the [P-Square Algorithm for Dynamic Calculation of Quantiles and Histograms without Storing Observations](http://www.cs.wustl.edu/~jain/papers/ftp/psqr.pdf) and other online statistical algorithms.

