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
      const path = `/api/entries/${this.id}`;
      // TODO: remove debug
      console.log(path);

      axios
        .get(path)
        .then(response => {
          // TODO: remove debug
          console.log(response);
          this.content = response.data.content;
        })
        .catch(error => {
          // TODO: remove debug
          console.log(error);
          this.content = error.response.data.message;
        });
    },
    updateEntry(id, content) {
      const path = `/api/entries/${id}`;

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
    // TODO: remove debug
    console.log(this.token);

    this.getEntry();
  }
};
</script>
