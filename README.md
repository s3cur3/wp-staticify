# NOTE: This software is pre-alpha. Do not attempt to use it in production yet.

wp-staticify is a tool for "scraping" your WordPress-based web site and turning it into a:

- dead simple,
- extremely fast,
- maximally secure

**static HTML** site. 

If your site is suitable to be completely static---that is, if it has *no* content that needs to be generated on-the-fly, and *all* users should see the same thing on *every* page, this tool can make your life a lot easier.

## Background: Why should you want a static site?

WordPress powers some [30%][study] of the world's web sites, yet it is *far* from trivial to set up a fast, secure site on WordPress. In fact, doing so is *so* difficult that there are loads of companies ([1], [2], [3], [etc.]) that have made a business out of making WordPress faster and at least a little more secure. (After all, if you *do* happen to have the technical chops to run a fast WordPress site yourself, you probably have better things to do---it's a full time job for a site of any significant size!) 

[study]: https://venturebeat.com/2018/03/05/wordpress-now-powers-30-of-websites/
[1]: https://wpengine.com
[2]: https://kinsta.com
[3]: https://getflywheel.com
[etc.]: https://www.bitcatcha.com/research/managed-wordpress-hosting-platforms/

There are three problems with this:

1. Managed hosting is *expensive*, because it's really hard. (E.g., for a site that gets 100,000 visits a month, you're looking at over $100/month.) If you're considering a "budget" managed hosting solution, you probably shouldn't waste your money.
2. There's a limit to how much faster even the best managed host can make your site. If the server has to run any amount of computation for every request, it's inevitably going to get bogged down at high levels of traffic.  
3. The best they can do on the security front is to a) do their best to lock down who can access the site, and b) install patches quickly. It might be *weeks* between the discovery of a major vulnerabilities and the time a patch is issued... not including the time it takes to get it installed on your site.

If [this massive list of serious vulnerabilities][plugin vulns] in seemingly benign plugins doesn't scare you, perhaps the list of recently patched [WordPress core vulnerabilities][core vulns] will. No matter how quickly your host installs updates, you would have been vulnerable to every single one of those for some amount of time.

[plugin vulns]: https://firstsiteguide.com/tools/free-fsg/hacked-dangerous-vulnerable-wordpress-plugins/ 
[core vulns]: https://www.cvedetails.com/vulnerability-list/vendor_id-2337/product_id-4096/

But, if you could instead run WordPress as an *editing* environment only, and "bake" your site down into static HTML, you could have all the power and flexibility of WordPress, rendered as fast as your server can spit files over the network, with *zero* vulnerabilities in the site itself.

In short, you take your attack surface from this (listed in *exponentially* increasing order of vulnerability):

1. OS
2. SFTP (you *are* using SFTP, not FTP, right?)
3. PHP
4. WordPress
5. WordPress Plugins

...down to this:

1. OS
2. SFTP

## FAQ

### Q: Does this support comments, since comments have to be dynamic?

**A**: Comments do indeed need to be dynamic, but you can use a plugin like [Disqus](https://wordpress.org/plugins/disqus-comment-system/) to *offload* the storage & processing of comments onto somebody else's server, then use Javascript to load them dynamically.

Depending on your use case, this might be an acceptable compromise.

### Q: My website doesn't use WordPress. Can I still create a static copy using wp-staticify?

**A**: Probably! ...but there *may* be intricacies to your own site's layout that are not handled correctly.

If you find that's the case, you're welcome to file a bug report (or even better, submit a pull request), but beware it may not fall under the scope of this project and therefore be deprioritized.   