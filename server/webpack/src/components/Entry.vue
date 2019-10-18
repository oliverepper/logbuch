<template>
  <Editable v-model="content" v-on:update="updateEntry(id, $event)" />
</template>

<script>
import axios from "axios";
import Editable from "./Editable.vue";

export default {
  name: "Entry",
  props: {
    id: {
      type: Number
    },
    token: {
      type: String
    }
  },
  components: {
    Editable
  },
  data() {
    return {
      content: "loading..."
    };
  },
  methods: {
    getEntry() {
      const path = `http://127.0.0.1:5000/api/entries/${this.id}`;

      axios
        .get(path)
        .then(response => {
          this.content = response.data.content;
        })
        .catch(error => {
          this.content = error.response.data.message;
        });
    },
    updateEntry(id, content) {
      const path = `http://localhost:5000/api/entries/${id}`;

      axios
        .put(path, {
          content: content
        })
        .catch(error => {
          this.content = error + error.response.data.message;
        });
    }
  },
  created() {
    axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;

    this.getEntry();
  }
};
</script>
