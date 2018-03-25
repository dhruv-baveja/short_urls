# What to do??

## Problem Statement
1. We need to generate Short URLs for given Long URLs and store the number of times the Short URL has been accessed. Ex: 
```
Long URL = https://www.hackerearth.com/challenge/hiring/hackerearth-python-developer-hiring-challenge/
Short URL = http://tiny.url/a2D3kfg9
```

2. From a user's point of view, getting a different Short URL everytime for the same Long URL is fine. The thing that matters is that the Short URL that he gets, should redirect him to the corresponding long URL

From this we can conclude a couple of facts:
### Facts:
- For each Short URL, we have only one Long URL
- Short URLs are unique across the space


## Problems
- **Short URL Generation**
- **Space**
- **Performance and Scalability for serving maximmum requestes, given the resources**



## Attempt 1
#### POSTGRES + SHA256 Hash
1. DB Table with 3 fields for storing the URLs map:
	1. short_url = unique string
	2. long_url = URL field
	3. count = Integer field

2. Straight forward architecture but poor performance and non-scalable

## Attempt 2
#### REDIS + SHA256 Hash
1. To achieve performance, my solution was to use **`REDIS`**, **in memory, O(1) lookup**

2. For each set of long_url, short_url and count. We have a 2 key-value pairs:

	- `<short_url>` : `<long_url>`
	- `<short_url>:count` : `<count>`

	Before deciding on the above structure, I tried out Hashes and Lists as well. But both of them were not fully supporting the needs. For example, there is no redis command to bulk get the hash values and in list, atomic increment wasn't directly available for a value in list.
3. I was extracting **8 random chars** out of SHA256 generated string but there was a fair chance of collision.
4. After updating the code and tests and trial running, I figured that the size of **RAM consumed for 10,000 sets of long_url, short_url and count**, assuming each URL to be of 512 bytes, **is around 1 GB**, which makes scaling the architecture very costly.


## FINAL SOLUTION
#### MONGO + REDIS + PRE GENERATED RANDOM SHORT URL POOL
1. Mongo is the database, with 2 collections:
	
	- Collection holding URL map
		- 3 keys: long_url, short_url, count
		- The collection is indexed(Ascending) using the field short_url. Look up time is O(log N) 
	- Collection holding pool of short URL
		- 2 keys: short_url, used 
		- This is a **pre-generated pool of 8 char strings** used to build the short URL which is populated by an **async task running every 2 hours** and making sure there is a minimum number of random strings(8 chars) available 
2. I decided to go against SHA256 to avoid computation and collision.
3. Redis is used for caching the mapping of **long_url to short_url** with a **ttl of 2 hours**. **A request asking for short url is returned from the cache if available, otherwise we create the short url getting one from the short url pool**
4. A random string generator which uses upper case alphabets, lower case alphabets and digits as the domain and generates a  random 8 char string which gives **218340105584896 unique short urls** 
5. **Response time** for a request having **1000 new long_urls** is **2.5 to 2.9 seconds**
6. Initially, we are dumping 10000 short urls every 2 hours in the pool but this number can be changed as we scale. We can decide this number as 2X the no. of requests the system can serve in 3 hours.
7. As we scale, we can also cache short url to long url mapping in Redis reducing look up time to O(1)

