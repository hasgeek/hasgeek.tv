// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import { Tabs, Tab } from 'vue-tabs-component';
import App from './App';
import router from './router';

Vue.config.productionTip = false;
Vue.config.devtools = true;

Vue.component('tabs', Tabs);
Vue.component('tab', Tab);

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App },
});
