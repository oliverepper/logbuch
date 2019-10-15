<template>
  <div class="Editable">
    <input type="test"
      v-if="edit"
      :value="valueLocal"
      @blur="valueLocal = $event.target.value; edit = false; $emit('input', valueLocal);"
      @keyup.enter="valueLocal = $event.target.value; edit = false; $emit('input', valueLocal);"
      v-focus />
    <div v-else="" @click="edit=true">{{ valueLocal}}</div>
  </div>
</template>

<script>
export default {
  name: 'Editable',
  props: ['value'],
  data() {
    return {
      edit: false,
      valueLocal: this.value,
    };
  },
  watch: {
    value() {
      this.valueLocal = this.value;
    },
    edit() {
      if (this.edit === false) {
        this.$emit('update', this.valueLocal);
      }
    },
  },
  directives: {
    focus: {
      inserted(el) {
        el.focus();
      },
    },
  },
};
</script>

<style scoped>
</style>
