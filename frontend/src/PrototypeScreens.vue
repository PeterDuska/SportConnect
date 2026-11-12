<script setup lang="ts">
import { computed, ref } from 'vue'

type Screen = 'rules' | 'event' | 'competitions' | 'group-settings' | 'admin'
type Match = { id: number; home: string; away: string; league: string; venue: string; start: number }
const props = defineProps<{ screen: Screen; match?: Match | null; groupName?: string }>()
const emit = defineEmits<{ close: [] }>()
const section = ref<'overview' | 'create' | 'detail'>('overview')
const adminTab = ref<'Matches' | 'Results' | 'Accounts' | 'Issues'>('Matches')
const adminForm = ref(false)
const adminSaved = ref(false)
const managingMembers = ref(false)
const sampleMemberVisible = ref(true)
const adminDetail = ref(false)
const attendance = ref('')
const visibility = ref('Public')
const competitionName = ref('')
const competition = ref('')
const title = computed(() => ({ rules: 'How scoring works', event: 'Matchday', competitions: 'Competitions', 'group-settings': 'Group settings', admin: 'Administration' })[props.screen])
function createCompetition() { if (!competitionName.value.trim()) return; competition.value = competitionName.value.trim(); competitionName.value = ''; section.value = 'detail' }
</script>

<template>
  <section class="extra-screen" :aria-label="title">
    <button type="button" class="detail-back" aria-label="Go back" @click="emit('close')"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5m0 0 6-6m-6 6 6 6"/></svg></button>
    <div class="extra-intro"><h1>{{ title }}</h1><p v-if="screen === 'competitions' || screen === 'group-settings'">{{ groupName }}</p><p v-else-if="screen === 'event' && match">{{ match.home }} vs {{ match.away }}</p><p v-else>Preview</p></div>

    <template v-if="screen === 'rules'">
      <div class="extra-panel"><h2>Scoring rules</h2><p>Example scoring only.</p><div class="rule-row"><span>Exact score</span><strong>3 pts</strong></div><div class="rule-row"><span>Correct winner or draw</span><strong>1 pt</strong></div><p class="sample-note">Points and tie-breaks are not final.</p></div>
    </template>

    <template v-else-if="screen === 'event' && match">
      <div class="extra-panel"><h2>At the venue</h2><div class="info-row"><span>Venue</span><strong>{{ match.venue }}</strong></div><div class="info-row"><span>Kickoff</span><strong>{{ new Intl.DateTimeFormat('en-GB', { dateStyle: 'medium', timeStyle: 'short' }).format(match.start) }}</strong></div><p class="sample-note">Sample event details.</p></div>
      <div class="extra-panel"><h2>Going to the match?</h2><div class="choice-row"><button v-for="choice in ['Going', 'Maybe', 'Not going']" :key="choice" type="button" :class="{ active: attendance === choice }" :aria-pressed="attendance === choice" @click="attendance = attendance === choice ? '' : choice">{{ choice }}</button></div><p class="sample-note">Preview only. Your answer is not shared or saved.</p></div>
    </template>

    <template v-else-if="screen === 'competitions'">
      <template v-if="section === 'overview'"><div class="extra-panel"><div class="detail-section-heading"><h2>Group competitions</h2><button class="text-button" type="button" @click="section = 'create'">Create</button></div><p v-if="!competition">No competitions yet.</p><button v-else class="extra-link" type="button" @click="section = 'detail'"><span>{{ competition }}<small>Preview competition</small></span><span aria-hidden="true">&#8250;</span></button></div><p class="sample-note">Competitions are previews and reset when you leave this screen.</p></template>
      <form v-else-if="section === 'create'" class="extra-panel extra-form" @submit.prevent="createCompetition"><h2>New competition</h2><label for="competition-name">Name</label><input id="competition-name" v-model="competitionName" required maxlength="60" placeholder="e.g. Weekend league"><label for="competition-scope">Matches</label><select id="competition-scope"><option>All group matches</option><option>Selected matches</option></select><p class="sample-note">Preview only. Match selection and scoring are not connected.</p><button class="primary" :disabled="!competitionName.trim()">Create preview</button><button class="text-button" type="button" @click="section = 'overview'">Cancel</button></form>
      <div v-else class="extra-panel"><h2>{{ competition }}</h2><p>Preview competition</p><div class="info-row"><span>Matches</span><strong>Not set</strong></div><div class="info-row"><span>Leaderboard</span><strong>Not available</strong></div><button type="button" class="text-button" @click="section = 'overview'">All competitions</button></div>
    </template>

    <template v-else-if="screen === 'group-settings'"><div class="extra-panel"><h2>Privacy</h2><div class="choice-row"><button v-for="option in ['Public', 'Private']" :key="option" type="button" :class="{ active: visibility === option }" :aria-pressed="visibility === option" @click="visibility = option">{{ option }}</button></div><p class="sample-note">Preview only. Privacy and membership changes are not saved.</p></div><div class="extra-panel"><div class="detail-section-heading"><h2>Manage members</h2><button type="button" class="text-button" @click="managingMembers = !managingMembers">{{ managingMembers ? 'Close' : 'Manage' }}</button></div><div v-if="managingMembers" class="manage-preview"><div v-if="sampleMemberVisible" class="info-row"><span>Sample member</span><button type="button" class="text-button" @click="sampleMemberVisible = false">Remove</button></div><p v-else class="sample-note">Sample member removed from this preview.</p><p class="sample-note">Preview only. No membership is changed.</p></div></div></template>

    <template v-else-if="screen === 'admin'">
      <p class="preview-banner">Design preview. Administration actions are not connected.</p>
      <div class="admin-tabs" role="group" aria-label="Administration sections"><button v-for="tab in (['Matches', 'Results', 'Accounts', 'Issues'] as const)" :key="tab" :class="{ active: adminTab === tab }" :aria-pressed="adminTab === tab" @click="adminTab = tab; adminForm = false; adminSaved = false; adminDetail = false">{{ tab }}</button></div>
      <div v-if="!adminForm && !adminDetail" class="extra-panel"><div class="detail-section-heading"><h2>{{ adminTab }}</h2><button v-if="adminTab === 'Matches' || adminTab === 'Results'" class="text-button" type="button" @click="adminForm = true">{{ adminTab === 'Matches' ? 'Add match' : 'Enter result' }}</button></div><p v-if="adminSaved" role="status" class="notice">Preview recorded on this screen only.</p><p>{{ adminTab === 'Matches' ? 'Create and update fixtures.' : adminTab === 'Results' ? 'Enter or correct final scores.' : adminTab === 'Accounts' ? 'Review and manage user accounts.' : 'Review reported problems and system status.' }}</p><button type="button" class="extra-link admin-example" @click="adminDetail = true"><span>{{ adminTab === 'Matches' || adminTab === 'Results' ? 'Slovan Bratislava vs Spartak Trnava' : adminTab === 'Accounts' ? 'Sample account' : 'Sample issue' }}<small>{{ adminTab === 'Matches' ? 'Sample fixture' : adminTab === 'Results' ? 'Awaiting result' : 'Preview only' }}</small></span><span aria-hidden="true">&#8250;</span></button></div>
      <div v-else-if="adminDetail" class="extra-panel"><h2>{{ adminTab === 'Accounts' ? 'Account details' : adminTab === 'Issues' ? 'Issue details' : adminTab === 'Matches' ? 'Fixture details' : 'Result details' }}</h2><p>{{ adminTab === 'Accounts' ? 'Sample account. Account status and access controls will appear here.' : adminTab === 'Issues' ? 'Sample issue. Status and resolution will appear here.' : 'Sample fixture. Editing and result history are not connected.' }}</p><button type="button" class="text-button" @click="adminDetail = false">Back to {{ adminTab.toLowerCase() }}</button></div>
      <form v-else class="extra-panel extra-form" @submit.prevent="adminForm = false; adminSaved = true"><h2>{{ adminTab === 'Matches' ? 'New match' : 'Enter result' }}</h2><template v-if="adminTab === 'Matches'"><label for="admin-home">Home team</label><input id="admin-home" required placeholder="Home team"><label for="admin-away">Away team</label><input id="admin-away" required placeholder="Away team"><label for="admin-date">Kickoff</label><input id="admin-date" type="datetime-local" required></template><template v-else><label for="admin-match">Match</label><select id="admin-match"><option>Slovan Bratislava vs Spartak Trnava</option></select><div class="admin-scores"><label>Home score<input type="number" min="0" max="99" required></label><label>Away score<input type="number" min="0" max="99" required></label></div></template><p class="sample-note">Preview only. Nothing is changed in the app.</p><button class="primary">Save preview</button><button class="text-button" type="button" @click="adminForm = false">Cancel</button></form>
    </template>
  </section>
</template>
