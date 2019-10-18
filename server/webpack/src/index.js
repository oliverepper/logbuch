import wrap from '@vue/web-component-wrapper';
import Vue from 'vue';
import Joke from './components/ChuckNorrisJoke.vue';

const wrappedElement = wrap(Vue, Joke);
window.customElements.define('logbuch-joke', wrappedElement);