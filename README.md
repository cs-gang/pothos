# pothos
Budget better.

![project showcase](/src/app/static/project-preview.gif)

## What it does
Pothos is a budget tracker. With Pothos, users can manage their finances effectively.

Users can input their income sources as well as their expenditure on a monthly basis. Pothos will display the data in a way where the user can effectively survey their financial habits and take appropriate action.
Users are also able to see the total income, the total expenditure and the remaining money they have.

## How we built it
Pothos was built using python and the Django framework, alongside Firebase in the backend. HTML, CSS, JavaScript and a CSS framework called Bulma was used to build the interface.

Vector images that have been used are from [undraw.co](https://undraw.co)

## Challenges we ran into
We ran into quite a couple of challenges. When faced with a timecrunch, we had to decide to drop some features and only focus on the core feature of our program.
We also faced various implementation problems which we took our time and patience solving.

## What we learned
- Project Planning is extremely important
- There is never enough time in a hackathon
- Communication between team mates is key

## Dev Environment Setup Guides
[General Guide to Poetry setup](https://gist.github.com/anand2312/910addd1b21c6f395afa2aa10fa387f7)

[General npm setup](https://gist.github.com/Windsmith/e98f7fb31590f8da041342fd40df0f86#setting-up-npm-but-not-for-the-first-time)

[Working with Bulma and nodesass](https://gist.github.com/Windsmith/96b3b0c1eea0bf26c2824b07fc15da89)

After following the above steps, running
> poetry run task runserver

from the root of the repository should run the Django development server (used for testing).
