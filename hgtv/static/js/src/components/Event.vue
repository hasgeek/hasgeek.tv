<template>
  <ul class="grid">
    <li v-for="channel in channels" class="grid__col-12 grid__col-xs-12 grid__col-sm-6 grid__col-lg-4">
        <div class="grid__cell">
          <a :href="channel.url" class="clickable-card">
            <div class="card">
              <div class="card__image-wrapper">
                  <img v-if="channel.banner_url" class="card__image" :src="channel.banner_url"/>
                  <div v-else class="card__image--default">
                    <img class="card__image" src="https://images.hasgeek.com/embed/file/5084bed3b3254c548bdcc119cd7b12ef" :alt="channel.title"/>
                    <p class="card__image__tagline">{{ channel.title }}</p>
                  </div>
                <div class="card__logo">
                  <div>
                    <img class="card__logo__img" :src="channel.logo"/>
                  </div>
                </div>
              </div>
              <div class="card__title">
                <h3 class="mui--text-title card__title__heading">{{ channel.title }}</h3>
              </div>
              <div v-if="channel.bio" class="card__body">
                <p>{{ channel.bio }}</p>
              </div>
              <div class="mui-divider"></div>
              <div class="card__footer">
                <a :href="channel.url" class="mui-btn mui-btn--flat mui-btn--accent card__footer__floatbtn">
                  <i class="material-icons play-btn">play_circle_filled</i>
                </a>
              </div>
            </div>
          </a>
        </div>
    </li>
  </ul>
</template>

<script>

export default {
  name: 'Event',
  props: ['channels'],
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
