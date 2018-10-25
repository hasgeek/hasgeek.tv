// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'vue-tabs-component/docs/resources/tabs-component.css';
import 'vue-snotify/styles/material.css';
import 'nprogress/nprogress.css';

import Vue from 'vue';
import Tabs from 'vue-tabs-component';
import Snotify from 'vue-snotify';
import VS2 from 'vue-script2';
import NProgress from 'nprogress';
import VueClazyLoad from 'vue-clazy-load';
import App from './App';
import router from './router';
import './assets/sass/app.sass';

Vue.config.productionTip = false;
Vue.config.devtools = true;

Vue.use(Tabs);
Vue.use(Snotify);
Vue.use(VS2);
Vue.use(VueClazyLoad);
Object.defineProperty(Vue.prototype, '$NProgress', { value: NProgress });

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App },
});
