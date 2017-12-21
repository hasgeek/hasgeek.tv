import Vue from 'vue';
import Router from 'vue-router';
import Home from '@/components/Home';
import Channel from '@/components/Channel';
import EditChannel from '@/components/EditChannel';
import ImportPlaylist from '@/components/ImportPlaylist';
import AddPlaylist from '@/components/AddPlaylist';
import AddVideo from '@/components/AddVideo';
import Playlist from '@/components/Playlist';
import EditPlaylist from '@/components/EditPlaylist';
import AddVideoToPlaylist from '@/components/AddVideoToPlaylist';
import ExtendPlaylist from '@/components/ExtendPlaylist';
import DeletePlaylist from '@/components/DeletePlaylist';
import Video from '@/components/Video';
import EditVideo from '@/components/EditVideo';
import DeleteVideo from '@/components/DeleteVideo';
import RemoveVideo from '@/components/RemoveVideo';

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
      path: '/:channel/edit',
      name: 'EditChannel',
      component: EditChannel,
    },
    {
      path: '/:channel/import',
      name: 'ImportPlaylist',
      component: ImportPlaylist,
    },
    {
      path: '/:channel/new',
      name: 'AddPlaylist',
      component: AddPlaylist,
    },
    {
      path: '/:channel/new/stream',
      name: 'AddVideo',
      component: AddVideo,
    },
    {
      path: '/:channel/:playlist',
      name: 'Playlist',
      component: Playlist,
    },
    {
      path: '/:channel/:playlist/edit',
      name: 'EditPlaylist',
      component: EditPlaylist,
    },
    {
      path: '/:channel/:playlist/new',
      name: 'AddVideoToPlaylist',
      component: AddVideoToPlaylist,
    },
    {
      path: '/:channel/:playlist/extend',
      name: 'ExtendPlaylist',
      component: ExtendPlaylist,
    },
    {
      path: '/:channel/:playlist/delete',
      name: 'DeletePlaylist',
      component: DeletePlaylist,
    },
    {
      path: '/:channel/:playlist/:video',
      name: 'Video',
      component: Video,
    },
    {
      path: '/:channel/:playlist/:video/edit',
      name: 'EditVideo',
      component: EditVideo,
    },
    {
      path: '/:channel/:playlist/:video/delete',
      name: 'DeleteVideo',
      component: DeleteVideo,
    },
    {
      path: '/:channel/:playlist/:video/remove',
      name: 'RemoveVideo',
      component: RemoveVideo,
    },
  ],
});
