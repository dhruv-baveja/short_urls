use short_urls
db.createCollection("url_map")
db.url_map.ensureIndex({"short_url": 1}, {"unique": true})
db.createCollection("short_urls_pool")
db.short_urls_pool.ensureIndex({"short_url": 1}, {"unique": true})
