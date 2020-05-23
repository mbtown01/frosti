# Getting started

## Useful links

* [Getting started guide for setting up a new project.
](https://jscomplete.com/learn/1rd-reactful/)
* [Getting started w/ your first react project
](https://jscomplete.com/learn/1rd-reactful)
* [Intro to grafana plugin development
](https://grafana.com/tutorials/build-a-panel-plugin/#1)
* [Numbers game from the React course on Pluralsight
](https://jscomplete.com/playground/rgs3.9)

## Setting up the initial plugin

Getting my first grafana plugin to work was rough.  The guide recommends
running the following to establish a new plugin:

```bash
npx @grafana/toolkit plugin:create my-plugin
```

Not sure if it's because Grafana v7 is so new, but this failed on a node-sass
dependency issue.  The only way I could make this work was to:

```bash
npm install -g --unsafe-perm=true --allow-root @grafana/toolkit
cd ${PROJECT_ROOT}/docker/grafana/plugins
grafana-toolkit plugin:create rpt
```

I realize that npx was created for this scenario -- you rarely if ever need
to run the grafana/toolkit.  However, to get things started it seemed
necessary.  I'm assuming that something is wrong with my setup or that there
is an `npx` option everyone is familiar with except me that would make it work.

## First build

To get things going, I followed the guide:

```bash
# Go get a Mt Dew, this took 10 minutes in a Docker container on my MacBook
yarn install

# This was a much more reasonable 3 minutes
yarn dev
```

## Dev time

You do *not* want to run `yarn dev` every time you change your code. Use
`yarn watch` to wait for changes and to dynamically transpile your code
