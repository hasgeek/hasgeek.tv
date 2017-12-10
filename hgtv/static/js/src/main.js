// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import Tab from 'vue-tabs-component';
import Toasted from 'vue-toasted';
import App from './App';
import router from './router';

Vue.config.productionTip = false;
Vue.config.devtools = true;

Vue.component('tab', Tab);
Vue.use(Toasted);
Vue.use(require('vue-script2'));

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App },
});
