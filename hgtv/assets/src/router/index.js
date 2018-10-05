import Vue from 'vue';
import Router from 'vue-router';

const Home = () => import('@/components/Home');
const Channel = () => import('@/components/Channel');
const EditChannel = () => import('@/components/EditChannel');
const ImportPlaylist = () => import('@/components/ImportPlaylist');
const AddPlaylist = () => import('@/components/AddPlaylist');
const AddVideo = () => import('@/components/AddVideo');
const Playlist = () => import('@/components/Playlist');
const EditPlaylist = () => import('@/components/EditPlaylist');
const AddVideoToPlaylist = () => import('@/components/AddVideoToPlaylist');
const ExtendPlaylist = () => import('@/components/ExtendPlaylist');
const DeletePlaylist = () => import('@/components/DeletePlaylist');
const Video = () => import('@/components/Video');
const EditVideo = () => import('@/components/EditVideo');
const DeleteVideo = () => import('@/components/DeleteVideo');
const RemoveVideo = () => import('@/components/RemoveVideo');

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
      path: '/:channel/new_playlist_ajax/:video',
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
