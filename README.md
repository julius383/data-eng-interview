# Overview

A technical interview project for data engineers.

The objective is to write a python program that will collect as many logos as you can across across a sample of websites.


# Objectives

* Write a program that will crawl a list of website and output their logo URLs.
* The program should read domain names on `STDIN` and write a CSV of domain and logo URL to `STDOUT`.
* A `websites.csv` list is included as a sample to crawl.
* You can't always get it right, but try to keep precision and recall as high as you can. Be prepared to explain ways you can improve. Bonus points if you can measure.
* Be prepared to discuss the bottlenecks as you scale up to millions of websites. You don't need to implement all the optimizations, but be able to talk about the next steps to scale it for production.
* Favicons aren't an adequate substitute for a logo, but if you choose, it's also valuable to extract as an additional field.
* Spare your time on implementing features that would be time consuming, but make a note of them so we can discuss the ideas.
* Please implement using python.
* Please keep 3rd party dependencies to a minimum, unless you feel there's an essential reason to add a dependency.
* We use [Nix](https://nixos.org/nix/) for package management. If you add your dependencies to `default.nix`, then it's easy for us to run your code. Install nix and launch the environment with `nix-shell` (works Linux, MacOS, and most unixes). Or install dependencies however you're comfortable and give us instructions.

There's no time limit. Spend as much or as little time on it as you'd like. Clone this git repository (don't fork), and push to a new repository when you're ready to share. We'll schedule a follow-up call to review.
