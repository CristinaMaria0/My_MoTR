<!-- Window is fixed, 102px, pointer cursor, gradual blurry effect on surrounding words. -->
<!--  Comprehension questions appear afterwards in the same slide -->

<template>
  <Experiment title="Mouse tracking for Reading" translate="no">

    <Screen :title="'Bun venit!'" class="instructions">
        <div style="width: 40em; margin: auto;">

        <div style="background-color: lightgrey; padding: 10px;">
            <b> Informații despre studiu </b>
        </div>
        <p>  Dorim să vă întrebăm dacă sunteți dispus să participați la proiectul nostru de cercetare. Participarea dumneavoastră este voluntară. Vă rugăm să citiți cu atenție textul de mai jos și să întrebați persoana care conduce studiul despre orice nu înțelegeți sau doriți să aflați.
  <br><br>
  <b>Ce este investigat și cum?</b> Acest studiu ne va ajuta să învățăm despre modul în care oamenii citesc. Va dura aproximativ 2 ore pentru a fi finalizat.

  <b>Ce trebuie să fac în calitate de participant?</b> Dacă alegeți să participați la studiu, veți folosi mouse-ul computerului pentru a citi propoziții în limba engleză și pentru a răspunde la întrebări despre acestea.

  <b>Cine a revizuit acest studiu?</b> Acest studiu a fost examinat de studenți ai Departamentului de Informatică de la Universitatea din București.

  <br>
  <div style="background-color: lightgrey; padding: 10px;">
    <b>Formular de Consimțământ</b>
  </div>
  <br>  Eu, participantul, confirm prin apăsarea butonului de mai jos: <br>
  <div style="padding-left: 30px">• Am citit și am înțeles informațiile despre studiu. Întrebările mele au primit răspuns complet și satisfăcător.</div>
  <div style="padding-left: 30px">• Mă conformez criteriilor de includere și excludere pentru participare descrise mai sus. Sunt conștient de cerințele și restricțiile care trebuie respectate în timpul studiului.</div>
  <div style="padding-left: 30px">• Am avut suficient timp pentru a decide asupra participării mele.</div>
  <div style="padding-left: 30px">• Particip la acest studiu în mod voluntar și sunt de acord ca datele mele personale să fie utilizate conform descrierii de mai sus.</div>
  <div style="padding-left: 30px">• Înțeleg că pot înceta participarea în orice moment.</div>
  <br>

  <br> Apăsând butonul de mai jos, vă exprimați consimțământul pentru participarea la acest studiu: <br><br>
  <br />
  <button 
    @click="$magpie.nextScreen()">
    Continuă
  </button>
</p>
</div>
</Screen>

<Screen :title="'Instrucțiuni'">

  <p>În acest studiu, veți citi texte scurte și veți răspunde la întrebări despre ele. Totuși, spre deosebire de citirea normală, textele vor fi încețoșate. Pentru a aduce textul în claritate, mutați mouse-ul peste acesta. Acordați-vă cât timp este necesar pentru a citi și înțelege textul. După ce ați terminat de citit,apasati butonul "Done" pentru a afisa intrebarea. Răspundeți la întrebarea de jos și apăsați "Next" pentru a continua.</p>
  <p> Va rog introduceti-va numele in casuta de mai jos</p>
  <label for="name" >Nume:</label>
  <input type="text" id="name" name="name" v-model="userName" required>
  <p v-if="nameError" style="color: red;">Numele este obligatoriu!</p>
  <!-- Updated Button with Validation -->
  <button @click="validateAndContinue">
    Continuă
  </button>
</Screen>

<template v-if="trials && trials.length">
   <Screen
     v-for="(trial, i) in trials"
     :key="i"
     class="main_screen"
     :progress="i / trials.length"
   >
       <Slide>
         <div class="oval-cursor"></div>
 
         <template>
           <div 
             v-if="showFirstDiv" 
             class="readingText" 
             @mousemove="moveCursor" 
             @mouseleave="changeBack"
           >
           <span
               v-for="(wordObj, index) in trial.words"
               :key="index"
               :data-index="index"
               :data-sentence-index="wordObj.sentenceIndex"
             >
               {{ wordObj.word }}
             </span>
           </div>
 
           <div class="blurry-layer" style="opacity: 0.3; filter: blur(3.5px); transition: all 0.3s linear 0s;"> 
             {{ trial.text }}
           </div>
         </template>
           <button v-if="showFirstDiv" style= "bottom:40%; transform: translate(-50%, -50%)" @click="toggleDivs" :disabled="!isCursorMoving">
           Done
           </button>
 
           <div v-else style = "position:absolute; bottom:15%; text-align: center; width: 100%; min-width: -webkit-fill-available;" >
             <template>
               <form>
                 <!-- comprehension questions and the response options -->
                 <div>{{ trial.question.replace(/ ?["]+/g, '') }}</div>
                 <template v-for='(word, index) of trial.response_options'>
                   <input 
                   :id="'opt_'+index" 
                   type="radio" 
                   :value="word" 
                   name="opt" 
                   v-model="$magpie.measurements.response"/>{{ word }}<br/>
                 </template>
               </form>
             </template>
           </div>
 
           <button v-if="$magpie.measurements.response" 
           style="transform: translate(-50%, -50%)" 
           @click="toggleDivs(); 
           $magpie.saveAndNextScreen()">
             Next
           </button>
         </Slide>
       </Screen>
    </template>
     <!--  Final screen -->
     <!-- <Screen class="download-screen">
       <div class="download-wrapper">
         <p class="download-message">{{ downloadMessage }}</p>
       </div>
     </Screen> -->
    <Screen class="download-screen" @hook:mounted="saveCsvToVolume"> 
      <p class="download-message">{{ downloadMessage }}</p>

    </Screen>

   </Experiment>
   </template>
<script>
// Load data from csv files as javascript arrays with objects
import localCoherence_list1 from '../trials/localCoherence_list1.tsv';
import propozitii_trial from '../trials/propozitii_trial.tsv';

import _ from 'lodash';

export default {
  name: 'App',
  data() {
    
    const lists = localCoherence_list1;
    const shuffledItems = _.shuffle(lists); 
    const trial_list= propozitii_trial;

    // const startExperimentScreen = { isSeparator: true };
    const trials=_.concat (trial_list, shuffledItems); //concatenate the two lists
    //const trials=[...trial_list, ...selectedItems]; 


    const updatedTrials = trials.map((trial, trialIndex) => {
      if (trial.isSeparator) {
        return trial; // Don't touch the separator, just return as-is
      }

      // const words = trial.text.split("  ");
      const words = trial.text.trim().split(/\s+/);

      return {
        ...trial,
        response_options: _.shuffle(`${trial.response_true}|${trial.response_distractors}`.replace(/ ?["]+/g, "").split("|")),
        TrueAnswer: trial.response_true, // Add the correct answer
        words: words.map((word, wordIndex) => ({
          word: word,
          sentenceIndex: trial.index_prop, // Store the sentence index for each word
          experiment:trial.experiment,
          }))
        };
      });
  return {
      isCursorMoving: false,
      trials: updatedTrials,
      userName: "",
      nameError: false,
      currentIndex: null,
      showFirstDiv: true,
      mousePosition: {
          x: 0,
          y: 0,
        },
      downloadMessage: '', // download message
  }},
  computed: {
  },
  mounted() {
  setInterval(this.saveData, 50);
  },
  methods: {
    validateAndContinue() {
    if (!this.userName.trim()) {
      this.nameError = true; // Show error message if name is empty
    } else {
      this.nameError = false;
      this.$magpie.nextScreen(); //  Move to the next screen
    }
  },
    changeBack() {
      this.$el.querySelector(".oval-cursor").classList.remove('grow');
      this.$el.querySelector(".oval-cursor").classList.remove('blank');
      this.currentIndex = null;
    },
    saveData() {
        if (this.currentIndex !== null) {
          const currentElement = this.$el.querySelector(`span[data-index="${this.currentIndex}"]`);
          if (currentElement) {
            const currentElementRect = currentElement.getBoundingClientRect();
            const sentenceIndex = currentElement.getAttribute('data-sentence-index'); // Get the sentence index
            // Find the trial (sentence) with the matching sentence index
            const currentTrial = this.trials.find(trial => trial.words.some(wordObj => wordObj.sentenceIndex === parseInt(sentenceIndex)));
            $magpie.addTrialData({
              experiment: currentTrial.experiment,
              sentenceIndex: sentenceIndex,
              Index: this.currentIndex,
              Word: currentElement.innerHTML,
              mousePositionX: this.mousePosition.x,
              mousePositionY: this.mousePosition.y,
              wordPositionTop: currentElementRect.top,
              wordPositionLeft: currentElementRect.left,
              wordPositionBottom: currentElementRect.bottom,
              wordPositionRight: currentElementRect.right,
              TrueAnswer:currentTrial.TrueAnswer, // Include the correct answer
              userName: this.userName,  // Add participant name
          });
        } else {
          $magpie.addTrialData({
              sentenceIndex: "NA",
              Index: this.currentIndex,
              mousePositionX: this.mousePosition.x,
              mousePositionY: this.mousePosition.y,
              TrueAnswer: "NA", // Fallback if no trial is found
              userName: this.userName,  //  Ensure name is always recorded

          });
          
        }
        // console.log("Current data", this.$data);
      }},
      saveCsvToVolume() {
        this.downloadMessage = "Please wait while your data is being downloaded...";

        const trialDataObj = $magpie.getAllData();
        console.log("All data", trialDataObj);

        if (!trialDataObj || typeof trialDataObj !== 'object') {
          console.warn("$magpie.trial_data is not ready or not an object:", trialDataObj);
          return;
        }

        const trials = Object.values(trialDataObj).flat();

        if (!trials.length) {
          console.warn("Flattened trial data is empty.");
          return;
        }

        console.log("Flattened trials:", trials);

          const headers = Object.keys(trials[0]);
          const csvRows = [
            headers.join(','),
            ...trials.map(row => headers.map(h => JSON.stringify(row[h] || '')).join(','))
          ];

          const csvContent = csvRows.join('\n');
          // const filename = `experiment_${Date.now()}.csv`;
          // ✅ Format file name: userName_YYYY-MM-DD_HH-mm.csv
          const date = new Date();
          const timestamp = date.toISOString().slice(0, 16).replace(/[:T]/g, '-');
          const namePart = this.userName.trim().replace(/\s+/g, "_") || "participant";
          const filename = `${namePart}_${timestamp}.csv`;

          console.log("🧠 Final CSV ready to save:", filename);
          fetch('/config.json')
            .then(res => res.json())
            .then(config => {
              const saveUrl = config.SAVE_RESULTS_URL;

              return fetch(saveUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ csv: csvContent, filename })
              });
    })
    .then(res => res.text())
    .then(msg => {
      console.log('✅ CSV saved:', msg);
      this.downloadMessage = "✅ Download finished successfully!";
    })
    .catch(err => {
      console.error('❌ Failed to save CSV:', err);
      this.downloadMessage = "❌ Something went wrong during download. Please try again!";
    });
},

    moveCursor(e) {
      this.isCursorMoving = true;
      this.$el.querySelector(".oval-cursor").classList.add('grow');
      let x = e.clientX;
      let y = e.clientY;
      const elementAtCursor= document.elementFromPoint(x, y).closest('span');
      if (elementAtCursor){
        this.$el.querySelector(".oval-cursor").classList.remove('blank');
        this.currentIndex = elementAtCursor.getAttribute('data-index');
      } else {
        this.$el.querySelector(".oval-cursor").classList.add('blank');
        const elementAboveCursor = document.elementFromPoint(x, y-10).closest('span');
        if (elementAboveCursor){
          this.currentIndex = elementAboveCursor.getAttribute('data-index');
        } else {
          this.currentIndex = -1;
        }
      }
      
      this.$el.querySelector(".oval-cursor").style.left = `${x+12}px`;
      this.$el.querySelector(".oval-cursor").style.top = `${y-6}px`;
      this.mousePosition.x = e.clientX;
      this.mousePosition.y = e.clientY;
      
    },
    toggleDivs() {
    this.showFirstDiv = !this.showFirstDiv;
    this.isCursorMoving = false;
    },
    getScreenDimensions() {
      return {
        window_inner_width: window.innerWidth,
        window_inner_height: window.innerHeight
      };
    }
}
};


</script>


<style>
  .experiment {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .main_screen {
    isolation: isolate;
    position: relative;
    width: 100%;
    height: auto;
    font-size: 18px;
    line-height: 55px;
  }
  .debugResults{
    width: 100%;
  }
  .readingText {
    /* z-index: 1; */
    position: absolute;
    color: white;
    text-align: left;
    font-weight: 450;
    cursor: pointer;
    padding-top: 2%;
    padding-bottom: 2%;
    padding-left: 8%;
    padding-right: 8%;
  }
  button {
    position: absolute;
    bottom: 0;
    left: 50%;
  }
  .oval-cursor {
    position: fixed;
    /* left: 10px; */
    z-index: 2;
    width: 1px;
    height: 1px;
    transform: translate(-50%, -50%);
    background-color: white;
    mix-blend-mode: difference;
    border-radius: 50%;
    pointer-events: none;
    transition: width 0.5s, height 0.5s;
  } 
  .oval-cursor.grow.blank {
    width: 80px;
    height: 38px;
  }
  .oval-cursor.grow {
    width: 102px;
    height: 38px;
    border-radius: 50%;
    box-shadow: 30px 0 8px -4px rgba(255, 255, 255, 0.1), -30px 0 8px -4px rgba(255, 255, 255, 0.1);
    background-color: rgba(255, 255, 255, 0.3);
    background-blend-mode: screen;
    pointer-events: none;
    transition: width 0.5s, height 0.5s;
    filter:blur(3px);
  }
  .oval-cursor.grow::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 70%;
    height: 70%;
    background-color: white;
    mix-blend-mode: normal;
    border-radius: 50%;
}
  .blurry-layer {
    position: absolute;
    pointer-events: none;
    color: black;
    text-align: left;
    font-weight: 450;
    padding-top: 2%;
    padding-bottom: 2%;
    padding-left: 8%;
    padding-right: 8%;
  }
  .download-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
  text-align: center;
  font-size: 1.2em;
}
.download-wrapper {
  background-color: #f5f5f5;
  padding: 2em;
  border-radius: 1em;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}
.download-message {
  margin-bottom: 1.5em;
  font-weight: bold;
  color: #333;
}

  * {
    user-select: none; /* Standard syntax */
    -webkit-user-select: none; /* Safari */
    -moz-user-select: none; /* Firefox */
    -ms-user-select: none; /* Internet Explorer/Edge */
    }
</style>
