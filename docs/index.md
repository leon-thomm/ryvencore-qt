# Welcome to the `ryvencore` documentation!

![](ryvencore_screenshot1.png)

Looking for a quick start? Visit the [Getting Started](/getting_started/) section.

## Project Idea

ryvencore is an easy to use framework for creating Qt based flow-based visual scripting editors for Python. ryvencore comes from the Ryven project, a flexible flow-based visual scripting environment for Python. The core concepts of Ryven are now implemented in ryvencore and will be the base also for Ryven itself from now on.

!!! info
    Since the biggest part of the code deals with management of the GUI (in particular drawing and interaction of nodes and flows) and a package not implementing this wouldn't contain much, ryvencore already provides you with those GUI classes, so it's not GUI independent, it depends on Qt (currently PySide2). There might be ways to integrate the PySide-based widgets of ryvencore into other GUI frameworks, but it is recommended that you use a Qt-based environment. Also notice that, compared to PyQt, PySide2 is licensed under the more flexible LGPL license.

!!! warning
    ryvencore is not a professional piece of software and sometimes there are major changes. If you have suggestions for improvement of the software, feel free to open discussions and PRs.

Besides essential GUI classes, ryvencore also provides you with a few convenience GUI classes which you may want to use, which only use ryvencore's public API, making it much easier to get started.

## Current State

In it's current state ryvencore is still experimental. It works well so far and I will use it to create a few more specific visual scripting editors for Python. But it's pretty much in alpha state.

## Resources

May I also point to the [website of the Ryven project](https://ryven.org) if you haven't been there already. And there's a [YouTube channel](https://www.youtube.com/channel/UCfpqNAOXv35bj_j_E_OyR_A), tutorials and stuff are planned.