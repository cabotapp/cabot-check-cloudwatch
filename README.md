Cloudwatch check for Cabot
==========================

Usage
=====

Setting AWS Credentials
-----------------------

You need to go into the django admin and create a `Cloudwatch Config` with your AWS_ACCESS_KEY and AWS_SECRET_KEY.

Creating a check
----------------

Once you have made a cloudwatch config you can create a check. Set the config first and then the metric dropdown should automatically fetch all the metrics from AWS. You can filter the list to find the one you need

Once you've selected the metric the dimensions select will autocomplete similarly - you have to select at least one dimension, but can select multiple

