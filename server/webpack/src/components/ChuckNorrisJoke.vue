<template>
  <p class="text-muted small">{{ message }}</p>
</template>

<script>
import axios from "axios";

export default {
  name: "ChuckNorris",
  props: {
      category: {
          type: String,
          default: "sport"
      }
  },
  data() {
    return {
      message: ""
    };
  },
  methods: {
    getJoke() {
      const path = `https://api.chucknorris.io/jokes/random?category=${this.category}`;
      console.log(path);
      axios
        .get(path)
        .then(res => {
          this.message = res.data.value;
        })
        .catch(err => {
          this.message = err;
        });
    }
  },
  created() {
    this.getJoke();
  }
};
</script>