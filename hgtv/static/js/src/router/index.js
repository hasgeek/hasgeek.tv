import Vue from 'vue';
import Router from 'vue-router';
import Home from '@/components/Home';
import Channel from '@/components/Channel';
import ImportForm from '@/components/ImportForm';
import Playlist from '@/components/Playlist';
import Video from '@/components/Video';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
    },
    {
      path: '/:channel',
      name: 'Channel',
      component: Channel,
    },
    {
      path: '/:channel/import',
      name: 'ImportForm',
      component: ImportForm,
    },
    {
      path: '/:channel/:playlist',
      name: 'Playlist',
      component: Playlist,
    },
    {
      path: '/:channel/:playlist/:video',
      name: 'Video',
      component: Video,
    },
  ],
});
