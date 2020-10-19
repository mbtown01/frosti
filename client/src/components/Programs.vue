<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Programs</h1>
        <hr />
        <br /><br />
        <alert :message="message" v-if="showMessage"></alert>
        <button
          type="button"
          class="btn btn-success btn-sm"
          v-b-modal.program-modal
        >
          Add Program...
        </button>
        <br /><br />
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Min</th>
              <th scope="col">Max</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(program, index) in programs" :key="index">
              <td>{{ program.name }}</td>
              <td>{{ program.comfortMin }}</td>
              <td>{{ program.comfortMax }}</td>
              <td>
                <div class="btn-group" role="group">
                  <button type="button" class="btn btn-warning btn-sm">
                    Configure
                  </button>
                  <button type="button" class="btn btn-danger btn-sm">
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal
      ref="addProgramModal"
      id="program-modal"
      title="Add a new program"
      hide-footer
    >
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
        <b-form-group
          id="form-name-group"
          label="Name:"
          label-for="form-name-input"
        >
          <b-form-input
            id="form-name-input"
            type="text"
            v-model="addProgramForm.name"
            required
            placeholder="Enter name"
          >
          </b-form-input>
        </b-form-group>
        <b-form-group
          id="form-comfortMin-group"
          label="Min:"
          label-for="form-comfortMin-input"
        >
          <b-form-input
            id="form-comfortMin-input"
            type="text"
            v-model="addProgramForm.comfortMin"
            required
            placeholder="Enter minimum temperature"
          >
          </b-form-input>
        </b-form-group>
        <b-form-group
          id="form-comfortMax-group"
          label="Min:"
          label-for="form-comfortMax-input"
        >
          <b-form-input
            id="form-comfortMax-input"
            type="text"
            v-model="addProgramForm.comfortMax"
            required
            placeholder="Enter minimum temperature"
          >
          </b-form-input>
        </b-form-group>

        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="danger">Reset</b-button>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import axios from 'axios';
import Alert from './Alert.vue';

export default {
  data() {
    return {
      programs: [],
      addProgramForm: {
        name: '',
        comfortMin: '',
        comfortMax: '',
      },
      message: '',
      showMessage: false,
    };
  },
  components: {
    alert: Alert,
  },
  methods: {
    getPrograms() {
      const path = 'http://localhost:5000/api/v1/programs';
      axios
        .get(path)
        .then((res) => {
          const programMap = res.data;
          const programList = [];
          // eslint-disable-next-line
          for (const [key, value] of Object.entries(programMap)) {
            value.name = key;
            programList.push(value);
          }
          this.programs = programList;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addProgram(payload) {
      const path = 'http://localhost:5000/api/v1/programs';
      axios.post(path, payload)
        .then(() => {
          this.getPrograms();
          this.message = 'Program added!';
          this.showMessage = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getPrograms();
        });
    },
    initForm() {
      this.addProgramForm.name = '';
      this.addProgramForm.comfortMin = '';
      this.addProgramForm.comfortMax = '';
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addProgramModal.hide();
      const payload = {
        name: this.addProgramForm.name,
        comfortMin: this.addProgramForm.comfortMin,
        comfortMax: this.addProgramForm.comfortMax,
      };
      this.addProgram(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addProgramModal.hide();
      this.initForm();
    },
  },
  created() {
    this.getPrograms();
  },
};
</script>
