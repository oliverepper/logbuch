import wrap from '@vue/web-component-wrapper';
import Vue from 'vue';
import Joke from './components/ChuckNorrisJoke.vue';
import Entry from './components/Entry.vue';

const joke = wrap(Vue, Joke);
const entry = wrap(Vue, Entry);

window.customElements.define('logbuch-joke', joke);
window.customElements.define('logbuch-entry', entry);