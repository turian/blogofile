import unittest
import tempfile
import shutil
import os
import BeautifulSoup
from .. import main

class TestContent(unittest.TestCase):
    def setUp(self):
        #Remember the current directory to preserve state
        self.previous_dir = os.getcwd()
        #Create a staging directory that we can build in
        self.build_path = tempfile.mkdtemp()
        #Change to that directory just like a user would
        os.chdir(self.build_path)
        #Reinitialize the configuration
        main.config.init()
    def tearDown(self):
        #go back to the directory we used to be in
        os.chdir(self.previous_dir)
        #Clean up the build directory
        shutil.rmtree(self.build_path)
    def testAutoPermalink(self):
        """Test to make sure post without permalink gets a good autogenerated one"""
        main.main("init simple_blog")

        #Write a post to the _posts dir:
        src = """---
title: This is a test post
date: 2009/08/16 00:00:00
---
This is a test post
"""
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site_url":"http://www.test.com",
            "blog_path":"/blog",
            "blog_auto_permalink_enabled": True,
            "blog_auto_permalink": "/blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","blog","2009","08",
                                     "16","this-is-a-test-post","index.html"
                                     )).read()
    def testHardCodedPermalinkUpperCase(self):
        """Permalink's set by the user should appear exactly as the user enters"""
        main.main("init simple_blog")
        #Write a post to the _posts dir:
        permalink = "http://www.BlogoFile.com/bLog/2009/08/16/This-Is-A-TeSt-Post"
        src = """---
title: This is a test post
permalink: %(permalink)s
date: 2009/08/16 00:00:00
---
This is a test post
""" % {'permalink':permalink}
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site_url":"http://www.test.com",
            "blog_path":"/blog",
            "blog_auto_permalink_enabled": True,
            "blog_auto_permalink": "/blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","bLog","2009","08",
                                     "16","This-Is-A-TeSt-Post","index.html"
                                     )).read()
    def testUpperCaseAutoPermalink(self):
        """Auto generated permalinks should have title and filenames lower case
        (but not the rest of the URL)"""
        main.main("init simple_blog")
        #Write a post to the _posts dir:
        src = """---
title: This is a test post
date: 2009/08/16 00:00:00
---
This is a test post without a permalink
"""
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site_url":"http://www.BlogoFile.com",
            "blog_path":"/Blog",
            "blog_auto_permalink_enabled": True,
            "blog_auto_permalink": "/Blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","Blog","2009","08",
                                     "16","this-is-a-test-post","index.html"
                                     )).read()
    
    def testPathOnlyPermalink(self):
        """Test to make sure path only permalinks are generated correctly"""
        main.main("init simple_blog")
        #Write a post to the _posts dir:
        permalink = "/blog/2009/08/16/this-is-a-test-post"
        src = """---
title: This is a test post
permalink: %(permalink)s
date: 2009/08/16 00:00:00
---
This is a test post
""" %{'permalink':permalink}
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site_url":"http://www.test.com",
            "blog_path":"/blog",
            "blog_auto_permalink_enabled": True,
            "blog_auto_permalink": "/blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","blog","2009","08",
                                     "16","this-is-a-test-post","index.html"
                                     )).read()

    def testFeedLinksAreURLs(self):
        """Make sure feed links are full URLs and not just paths"""
        main.main("init simple_blog")
        #Write a post to the _posts dir:
        permalink = "/blog/2009/08/16/test-post"
        src = """---
title: This is a test post
permalink: %(permalink)s
date: 2009/08/16 00:00:00
---
This is a test post
""" %{'permalink':permalink}
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site_url":"http://www.test.com",
            "blog_path":"/blog",
            "blog_auto_permalink_enabled": True,
            "blog_auto_permalink": "/blog/:year/:month/:day/:title" }
        main.main("build")
        feed = open(os.path.join(self.build_path,"_site","blog","feed",
                                 "index.xml")).read()
        soup = BeautifulSoup.BeautifulStoneSoup(feed)
        for link in soup.findAll("link"):
            assert(link.contents[0].startswith("http://"))

    def testCategoryLinksInPosts(self):
        """Make sure category links in posts are correct"""
        main.main("init simple_blog")
        main.config.override_options = {
            "site_url":"http://www.test.com",
            "blog_path":"/blog"
            }
        #Write a blog post with categories:
        src = """---
title: This is a test post
categories: Category 1, Category 2
date: 2009/08/16 00:00:00
---
This is a test post
"""
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.main("build")
        #Open up one of the permapages:
        page = open(os.path.join(self.build_path,"_site","blog","2009",
                                 "08","16","this-is-a-test-post","index.html")).read()
        soup = BeautifulSoup.BeautifulStoneSoup(page)
        print soup.findAll("a")
        assert soup.find("a",attrs={'href':'/blog/category/category-1'})
        assert soup.find("a",attrs={'href':'/blog/category/category-2'})

