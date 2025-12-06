---
title: "Helping a local restaurant (and training my frontend skills) over Golden Week"
date: 2020-05-10T22:30:00+09:00
tags: [tech, frontend]
---

# Introduction

Over Golden Week I finally tried my hand at a fairly real frontend project. I had avoided serious frontend work for years, but decided it was time to understand the feel of it. As a bonus, I could help out a favorite restaurant that was struggling in the current situation. They had started takeout but found it hard to update their website by themselves. We had joked before about me building it, so I used the holiday to actually give it a shot.

### Deliverable

The site I built during GW is [here](https://vineria-sorcuore.netlify.app). For a first attempt it came out pretty nicely. It is MIT-licensed, so feel free to reuse it for other restaurants.  
https://github.com/utam0k/vineria-sorcuore

### Constraints

1. Make menu updates easy without us stepping in.
1. Give it a reasonably restaurant-like design.
1. Responsive layout.
1. Cost: 0 yen[^*]

[^*]: I did this as study, so of course I charged nothing. In exchange they allowed me to open-source it.

### Motivation

- I have more chances to touch frontend at work.
- I wanted to finally tackle the area I had avoided.
- I found a good real-world theme.

# Tools and services used

### Storybook

Since several of us worked on it, we used [Storybook](https://storybook.js.org) to review PRs. We created an `@deploy-storybook` command via GitHub Actions; when it appears in a PR comment, it triggers deployment to gh-pages. That workflow was super handy and seems reusable elsewhere.
{{% figure src="deploy-storybook.png" %}}

### Making menu updates easy

This was the most distinctive part. In short, we turned Google Sheets into our API.

{{% figure src="takeout.png" %}}

The pain point was response speed. Google Apps Script has caching, so we used that to keep responses around one second. While waiting for responses we learned to use skeleton loading states to mask the delay.

### Images

A restaurant site needs good photos. We used [Google Photos](https://www.google.com/intl/ja/photos/about/) as image hosting. It's free and easy for the owners to add and update pictures themselves, which is why we chose it.

### next.js

Handy framework for building with React.

### netlify

We used Netlify for hosting. We just needed something solid in the free tier—no deeper reason.  
https://www.netlify.com

### chakra-ui

Made it easy to get a decent design. It was especially helpful for responsive layouts.  
https://chakra-ui.com

### Pair-programming tools

- VSCode Live Share — extremely convenient; the shared server feature blew me away. (I normally use vim.)
- Slack calls — drawing together is great for frontend design discussions.

## Still to do

We still need to decide on buying a domain. Since that costs money, I explained pros/cons and left the decision to them. The idea is that even if we get hit by a bus, someone else could rebuild the site without changing domains.

# Thanks

I paired with my frontend-pro friend [succie](https://twitter.com/succie319) and learned a ton—thank you! Contributors [chao](https://twitter.com/chao7150) and [asakura](https://twitter.com/asakura_dev) also helped—much appreciated. We used *[HTML & CSS and Web Design in One Book]* (Japanese) as a reference.

# Closing

We removed `robots.txt` and released it; the restaurant staff seemed happy. We exchanged images and wording over Instagram DMs. After going through the whole process I feel like I can now write frontend “by feel,” so I’m glad I tried. The ecosystem and CSS were especially tough—flex is hard! If you have suggestions for doing this better, please let me know; PRs welcome. By the way, work resumes tomorrow—really?
