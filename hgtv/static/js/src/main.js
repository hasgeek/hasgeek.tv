// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'vue-tabs-component/docs/resources/tabs-component.css';
import 'vue-snotify/styles/material.css';
import 'nprogress/nprogress.css';

import Vue from 'vue';
import Tab from 'vue-tabs-component';
import Snotify from 'vue-snotify';
import VS2 from 'vue-script2';
import NProgress from 'nprogress';
import App from './App';
import router from './router';

Vue.config.productionTip = false;
Vue.config.devtools = true;

Vue.component('tab', Tab);
Vue.use(Snotify);
Vue.use(VS2);
Object.defineProperty(Vue.prototype, '$NProgress', { value: NProgress });

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App },
});
