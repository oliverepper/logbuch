<template>
  <div>
    {{ msg }}
    <div v-bind:key="log.id" v-for="log in logs">
      <Editable v-model="log.title" v-on:update="updateLog(log.id, $event)" />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Editable from "./Editable.vue";

export default {
  name: "Log",
  components: {
    Editable
  },
  data() {
    return {
      msg: "",
      logs: []
    };
  },
  methods: {
    getLogs() {
      const path = "http://127.0.0.1:5000/api/logs";

      axios
        .get(path)
        .then(res => {
          this.logs = res.data.logs;
        })
        .catch(error => {
          this.msg = error.response.data.message;
        });
    },
    updateLog(id, title) {
      const path = `http://localhost:5000/api/logs/${id}`;

      axios
        .put(path, {
          title: title
        })
        .then((response) => {
          this.msg = response.data.message;
          this.getLogs();
        })
        .catch(error => {
          this.msg = error + error.response.data.message;
        });
    }
  },
  created() {
    const token = "0T0ZfGWSdGvdIWQD/h9D46+7M3iRxSh08557KqUhnnA=";
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;

    this.getLogs();
  }
};
</script>
