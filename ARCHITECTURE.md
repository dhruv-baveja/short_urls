# What to do??

## Problem Statement
1. We need to generate a Short URLs for Long URLs and store the number of times the Short URL has been accessed. Ex: 

2. From a user's point of view, getting a different Short URL everytime for the same Long URL is fine. The thing that matters to him is that the Short URL that he gets, should redirect him to the corresponding long URL

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

	Before deciding on the above structure, I tried out hashes and lists as well. But both of these were not fully supporting the needs. For example, there is no redis command to bulk get the hash values and in list, atomic increment wasn't directly available for a value in list.

3. After updating the code and tests and trial running, I figured that the size of **RAM consumed for 10,000 sets of long_url, short_url and count**, assuming each URL to be of 512 bytes, **is around 1 GB**, which makes scaling the architecture very costly.



## FINAL SOLUTION
#### MONGO + REDIS + PRE GENERATED RANDOM SHORT URL POOL
1. Mongo is the database, with 2 collections:
	
	- url_map
		- 3 keys: long_url, short_url, count
		- short_url is indexed and unique for fast lookup
	- short_url_pool
		- 2 keys: short_url, used
		- This is a **pre-generated pool of short_urls** which is populated by an **async task running every 2 hours** and checks if the **pool size(configurable)** is less than a **minimum buffer size(configurable)**, then it will populate the pool.   

2. Redis is used for caching the mapping of **long_url to short_url** with a **ttl of 2 hours**. **If a long_url request comes in, we first check in the cache if a short_url corresponding to it already exists, then we respond with that otherwise we get a short url from the pool and associate it with the requested long url.**
3. A random string generator which uses upper case alphabets, lower case alphabets and digits as the domain and generates a  random 8 char string which gives **218340105584896 unique short urls** 
4. **Response time** for a request having **1000 new long_urls** is **2.5 to 2.9 seconds**
5. Right now we are dumping 10000 short urls every 2 hours in the pool but this number needs to be changed as we scale depending upon the underlying system resources.
6. As we scale, we can also cache short url to long url mapping.
