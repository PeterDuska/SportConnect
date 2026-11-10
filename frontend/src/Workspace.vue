<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref } from 'vue'
import PrototypeScreens from './PrototypeScreens.vue'
defineProps<{ name: string; email: string; busy: boolean }>()
defineEmits<{ logout: [] }>()
type Page = 'Matches' | 'My bets' | 'Communities' | 'Rankings'
type Match = { id: number; home: string; away: string; league: string; venue: string; start: number }
const page = ref<Page>('Matches')
const tabs: Page[] = ['Matches', 'My bets', 'Communities', 'Rankings']
const matchFilter = ref<'Upcoming' | 'Closed'>('Upcoming')
const picksFilter = ref<'Upcoming' | 'Closed'>('Upcoming')
const tabDirection = ref<'forward' | 'backward'>('forward')
function selectMatchFilter(item: 'Upcoming' | 'Closed', isPicks: boolean) {
  const current = isPicks ? picksFilter : matchFilter
  if (current.value === item) return
  tabDirection.value = item === 'Closed' ? 'forward' : 'backward'
  current.value = item
}
const matchLeague = ref('All leagues')
const picksLeague = ref('All leagues')
const matchSearch = ref('')
const picksSearch = ref('')
const filtersOpen = ref(false)
const filtersClosing = ref(false)
let filterCloseTimer: ReturnType<typeof setTimeout> | undefined
onUnmounted(() => clearTimeout(filterCloseTimer))
const filterDialog = ref<HTMLDialogElement | null>(null)
const filterButton = ref<HTMLButtonElement | null>(null)
const draftLeague = ref('All leagues')
const draftSearch = ref('')
function openFilters() {
  draftLeague.value = page.value === 'Matches' ? matchLeague.value : picksLeague.value
  draftSearch.value = page.value === 'Matches' ? matchSearch.value : picksSearch.value
  filtersOpen.value = true
  filterDialog.value?.showModal()
}
function closeFilters() {
  if (filtersClosing.value) return
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { filterDialog.value?.close(); return }
  filtersClosing.value = true
  filterCloseTimer = setTimeout(() => filterDialog.value?.close(), 180)
}
function filtersClosed() { filtersOpen.value = false; filtersClosing.value = false; filterButton.value?.focus() }
function applyFilters() {
  if (page.value === 'Matches') { matchLeague.value = draftLeague.value; matchSearch.value = draftSearch.value }
  else { picksLeague.value = draftLeague.value; picksSearch.value = draftSearch.value }
  closeFilters()
}
const extraScreen = ref<'rules' | 'event' | 'competitions' | 'group-settings' | 'admin' | null>(null)
const rankingPeriod = ref('All time')
const navIcons: Record<Page, string> = {
  Matches: 'M8 3v4m8-4v4M4 10h16M5 5h14a1 1 0 0 1 1 1v14H4V6a1 1 0 0 1 1-1Z',
  'My bets': 'm5 12 4 4L19 6',
  Communities: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m20 0v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z',
  Rankings: 'M8 21V11H3v10m13 0V3h-5v18m10 0v-7h-5',
}
const now = ref(Date.now())
const timer = window.setInterval(() => now.value = Date.now(), 1000)
onUnmounted(() => clearInterval(timer))
const base = new Date(); base.setHours(18, 30, 0, 0); if (base.getTime() <= Date.now()) base.setDate(base.getDate() + 1)
const matches: Match[] = [
  { id: 1, home: 'Slovan Bratislava', away: 'Spartak Trnava', league: 'Niké liga', venue: 'Tehelné pole, Bratislava', start: +base },
  { id: 5, home: 'Manchester City', away: 'Chelsea', league: 'Premier League', venue: 'Etihad Stadium, Manchester', start: +base + 1800000 },
  { id: 6, home: 'Bayern Munich', away: 'Borussia Dortmund', league: 'Bundesliga', venue: 'Allianz Arena, Munich', start: +base + 3600000 },
  { id: 7, home: 'Inter Milan', away: 'AC Milan', league: 'Serie A', venue: 'San Siro, Milan', start: +base + 5400000 },
  { id: 8, home: 'Paris Saint-Germain', away: 'Marseille', league: 'Ligue 1', venue: 'Parc des Princes, Paris', start: +base + 7200000 },
  { id: 9, home: 'Atletico Madrid', away: 'Sevilla', league: 'La Liga', venue: 'Metropolitano, Madrid', start: +base + 9000000 },
  { id: 10, home: 'Juventus', away: 'Napoli', league: 'Serie A', venue: 'Allianz Stadium, Turin', start: +base + 10800000 },
  { id: 11, home: 'Ajax', away: 'PSV Eindhoven', league: 'Eredivisie', venue: 'Johan Cruyff Arena, Amsterdam', start: +base + 12600000 },
  { id: 12, home: 'Benfica', away: 'Porto', league: 'Primeira Liga', venue: 'Estadio da Luz, Lisbon', start: +base + 14400000 },
  { id: 13, home: 'Celtic', away: 'Rangers', league: 'Scottish Premiership', venue: 'Celtic Park, Glasgow', start: +base + 16200000 },
  { id: 14, home: 'Bayer Leverkusen', away: 'RB Leipzig', league: 'Bundesliga', venue: 'BayArena, Leverkusen', start: +base + 18000000 },
  { id: 2, home: 'FC Barcelona', away: 'Real Madrid', league: 'La Liga', venue: 'Barcelona', start: +base + 21600000 },
  { id: 3, home: 'Liverpool', away: 'Arsenal', league: 'Premier League', venue: 'Anfield, Liverpool', start: +base + 86400000 },
  { id: 4, home: 'Žilina', away: 'Dunajská Streda', league: 'Niké liga', venue: 'Štadión pod Dubňom', start: +base - 86400000 },
]
const leagues = ['All leagues', ...new Set(matches.map(match => match.league))]
const picks = ref<Record<number, { home: number; away: number }>>({})
const shown = computed(() => matches.filter(m => {
  const isPicks = page.value === 'My bets'
  const upcoming = m.start > now.value
  const league = isPicks ? picksLeague.value : matchLeague.value
  const search = (isPicks ? picksSearch.value : matchSearch.value).trim().toLocaleLowerCase()
  const matchesFilters = (league === 'All leagues' || m.league === league) &&
    (!search || `${m.home} ${m.away}`.toLocaleLowerCase().includes(search))
  return matchesFilters && (isPicks
    ? !!picks.value[m.id] && (picksFilter.value === 'Upcoming' ? upcoming : !upcoming)
    : matchFilter.value === 'Upcoming' ? upcoming : !upcoming)
}))
const selected = ref<Match | null>(null)
const detailHeading = ref<HTMLElement | null>(null)
type Reaction = 'like' | 'dislike'
const reactions = ref<Record<string, Reaction | undefined>>({})
const sampleMembers: Record<number, string[]> = { 2: ['Pavol K.', 'Nina S.'] }
const sampleScores: Record<number, Record<number, [number, number][]>> = {
  2: { 1: [[1, 0], [2, 2]], 2: [[0, 1], [2, 1]], 3: [[3, 1], [0, 0]] },
}
type MemberPick = { name: string; home: number; away: number }
function memberPicks(groupId: number, matchId: number): MemberPick[] {
  const scores = sampleScores[groupId]?.[matchId] ?? []
  return (sampleMembers[groupId] ?? []).flatMap((name, index) => {
    const score = scores[index]
    return score ? [{ name, home: score[0], away: score[1] }] : []
  })
}
function reactionKey(groupId: number, matchId: number, member: string) { return `${groupId}-${matchId}-${member}` }
function toggleReaction(groupId: number, matchId: number, member: string, reaction: Reaction) {
  const key = reactionKey(groupId, matchId, member)
  reactions.value[key] = reactions.value[key] === reaction ? undefined : reaction
}
const home = ref<number | string>('')
const away = ref<number | string>('')
function adjustScore(side: 'home' | 'away', change: number) {
  const score = side === 'home' ? home : away
  const current = score.value === '' ? -1 : Number(score.value)
  score.value = Math.max(0, Math.min(99, (Number.isFinite(current) ? current : -1) + change))
}
const notice = ref('')
const saveCount = ref(0)
const showSaveFlash = ref(false)
const showSaveToast = ref(false)
let saveFlashTimer: ReturnType<typeof setTimeout> | undefined
let saveToastTimer: ReturnType<typeof setTimeout> | undefined
onUnmounted(() => { clearTimeout(saveFlashTimer); clearTimeout(saveToastTimer) })
const valid = computed(() => [home.value, away.value].every(v => v !== '' && Number.isInteger(Number(v)) && Number(v) >= 0 && Number(v) <= 99))
async function open(m: Match, groupId?: number) { matchGroupId.value = groupId ?? groups.value[0]?.id ?? null; selected.value = m; home.value = picks.value[m.id]?.home ?? ''; away.value = picks.value[m.id]?.away ?? ''; notice.value = ''; await nextTick(); detailHeading.value?.focus() }
function save() {
  if (!selected.value || !valid.value) return
  if (selected.value.start <= now.value) { notice.value = 'Kickoff has passed. This match is locked.'; return }
  picks.value[selected.value.id] = { home: Number(home.value), away: Number(away.value) }
  saveCount.value++
  showSaveFlash.value = true
  clearTimeout(saveFlashTimer)
  saveFlashTimer = setTimeout(() => { showSaveFlash.value = false }, 700)
  showSaveToast.value = true
  clearTimeout(saveToastTimer)
  saveToastTimer = setTimeout(() => { showSaveToast.value = false }, 3500)
  notice.value = ''
}
function time(m: Match) { return new Intl.DateTimeFormat('en-GB', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }).format(m.start) }
const scope = ref('Global')
type Group = { id: number; name: string; sample: boolean; invited: string[] }
const groups = ref<Group[]>([
  { id: 2, name: 'Bratislava matchdays', sample: true, invited: [] },
])
const selectedGroup = ref<Group | null>(null)
const matchGroupId = ref<number | null>(null)
const groupMatchId = ref<number>(matches[0]?.id ?? 0)
const matchCommunityPicks = computed(() => selected.value && matchGroupId.value !== null ? memberPicks(matchGroupId.value, selected.value.id) : [])
const groupMatch = computed(() => matches.find(match => match.id === groupMatchId.value))
const selectedGroupPicks = computed(() => selectedGroup.value ? memberPicks(selectedGroup.value.id, groupMatchId.value) : [])
const groupTab = ref<'Members' | 'Rankings' | 'Bets'>('Members')
const groupHeading = ref<HTMLElement | null>(null)
const inviteName = ref('')
const inviteOpen = ref(false)
async function openGroup(group: Group, invite = false) {
  selectedGroup.value = group
  groupTab.value = 'Members'
  groupMatchId.value = matches[0]?.id ?? 0
  inviteOpen.value = invite
  inviteName.value = ''
  notice.value = ''
  await nextTick()
  groupHeading.value?.focus()
}
function addPreviewMember() {
  const value = inviteName.value.trim()
  if (!value || !selectedGroup.value) return
  selectedGroup.value.invited.push(value)
  inviteName.value = ''
  notice.value = 'Added to this preview. No invitation was sent.'
}
function closeGroup() { selectedGroup.value = null; inviteOpen.value = false; notice.value = '' }
function closeMatch() { selected.value = null; notice.value = '' }
const groupName = ref('')
const creatingGroup = ref(false)
const showingProfile = ref(false)
const profileHeading = ref<HTMLElement | null>(null)
const profileButton = ref<HTMLButtonElement | null>(null)
async function openProfile() {
  showingProfile.value = true
  notice.value = ''
  await nextTick()
  profileHeading.value?.focus()
}
async function closeProfile() {
  showingProfile.value = false
  await nextTick()
  profileButton.value?.focus()
}
const createHeading = ref<HTMLElement | null>(null)
const createButton = ref<HTMLButtonElement | null>(null)
async function openCreateGroup() {
  creatingGroup.value = true
  groupName.value = ''
  notice.value = ''
  await nextTick()
  createHeading.value?.focus()
}
async function closeCreateGroup() {
  creatingGroup.value = false
  groupName.value = ''
  await nextTick()
  createButton.value?.focus()
}
async function createGroup() {
  const title = groupName.value.trim()
  if (!title) return
  const group: Group = { id: Date.now(), name: title, sample: false, invited: [] }
  groups.value.push(group)
  creatingGroup.value = false
  groupName.value = ''
  await openGroup(group, true)
}
</script>

<template>
  <div class="workspace">
    <div v-if="showSaveFlash" :key="saveCount" class="save-flash" aria-hidden="true"></div>
    <div v-if="showSaveToast" :key="saveCount" class="save-toast save-confirmation" role="status"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg><span>Bet saved</span></div>
    <nav class="workspace-nav" aria-label="Main navigation"><button v-for="tab in tabs" :key="tab" :class="{ active: page === tab && !showingProfile }" :aria-current="page === tab && !showingProfile ? 'page' : undefined" @click="page = tab; notice = ''; selected = null; selectedGroup = null; creatingGroup = false; showingProfile = false; groupName = ''; filtersOpen = false; extraScreen = null"><svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="navIcons[tab]" /></svg><span>{{ tab === 'Communities' ? 'Groups' : tab }}</span><span v-if="tab === 'My bets' && Object.keys(picks).length" class="count">{{ Object.keys(picks).length }}</span></button><button ref="profileButton" type="button" :class="{ active: showingProfile }" :aria-current="showingProfile ? 'page' : undefined" @click="selected = null; selectedGroup = null; creatingGroup = false; groupName = ''; extraScreen = null; openProfile()"><svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4.5 21v-1.5a7.5 7.5 0 0 1 15 0V21"/></svg><span>Profile</span></button></nav>
    <PrototypeScreens v-if="extraScreen" :key="extraScreen" :screen="extraScreen" :match="selected" :group-name="selectedGroup?.name" @close="extraScreen = null" />
    <div v-else-if="!selected && !selectedGroup && !creatingGroup && !showingProfile" class="workspace-content">
      <h1 class="sr-only">{{ page }}</h1>

      <p v-if="notice" class="notice" role="status">{{ notice }}</p>
      <template v-if="page === 'Matches' || page === 'My bets'">
        <div class="section-toolbar">
          <div v-if="page === 'Matches'" class="filter-tabs" role="group" aria-label="Filter matches"><button v-for="item in (['Upcoming', 'Closed'] as const)" :key="item" :aria-pressed="matchFilter === item" :class="{ active: matchFilter === item }" @click="selectMatchFilter(item, false)">{{ item }}</button></div>
          <div v-else class="filter-tabs" role="group" aria-label="Filter your bets"><button v-for="item in (['Upcoming', 'Closed'] as const)" :key="item" :aria-pressed="picksFilter === item" :class="{ active: picksFilter === item }" @click="selectMatchFilter(item, true)">{{ item }}</button></div>
          <button ref="filterButton" class="filter-toggle" type="button" aria-label="Filters" :aria-expanded="filtersOpen" aria-controls="match-filter-panel" @click="openFilters"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 7h10m4 0h2M4 17h2m4 0h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/></svg><span v-if="(page === 'Matches' ? matchLeague !== 'All leagues' || matchSearch.trim() : picksLeague !== 'All leagues' || picksSearch.trim())" class="filter-indicator" aria-label="Filters active">&#8226;</span></button>
        </div>
        <dialog id="match-filter-panel" ref="filterDialog" class="filter-dialog" :class="{ closing: filtersClosing }" aria-labelledby="filter-title" @close="filtersClosed" @cancel.prevent="closeFilters" @click.self="closeFilters">
          <form class="filter-form" @submit.prevent="applyFilters">
            <div class="filter-dialog-heading"><div><span class="filter-eyebrow">{{ page === 'Matches' ? 'MATCHES' : 'MY BETS' }}</span><h2 id="filter-title">Filters</h2></div><button type="button" class="filter-close" aria-label="Close filters" @click="closeFilters"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button></div>
            <label><span>League</span><span class="filter-field filter-select"><select v-model="draftLeague"><option v-for="league in leagues" :key="league">{{ league }}</option></select><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m7 10 5 5 5-5"/></svg></span></label>
            <label><span>Team</span><span class="filter-field filter-search"><svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 4 4"/></svg><input v-model="draftSearch" type="search" placeholder="Search team"></span></label>
            <div class="filter-actions"><button class="filter-reset" type="button" @click="draftLeague = 'All leagues'; draftSearch = ''">Clear</button><button class="primary filter-submit" type="submit"><svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 4 4"/></svg><span>Search</span></button></div>
          </form>
        </dialog>
        <div class="match-results-viewport"><div :key="`${page}-${page === 'Matches' ? matchFilter : picksFilter}`" class="match-results" :class="`slide-${tabDirection}`"><div class="match-list"><button v-for="m in shown" :key="m.id" type="button" class="match-row match-row-button" :aria-label="`View ${m.home} vs ${m.away}`" @click="open(m)"><span class="match-meta"><span>{{ m.league }}</span><span>{{ time(m) }}</span></span><span class="match-body"><span class="teams"><span class="team-home">{{ m.home }}</span><span class="versus">vs</span><span class="team-away">{{ m.away }}</span></span><span v-if="picks[m.id]" class="pick-score">Your bet <strong>{{ picks[m.id]?.home }} : {{ picks[m.id]?.away }}</strong></span><span v-else class="match-chevron" aria-hidden="true">&#8250;</span></span></button></div>
        <div v-if="!shown.length" class="empty-state"><h2>{{ page === 'My bets' ? (picksFilter === 'Closed' ? 'No closed bets found.' : 'No upcoming bets found.') : 'No matches found.' }}</h2><button class="text-button" @click="page = 'Matches'; matchFilter = 'Upcoming'; matchLeague = 'All leagues'; matchSearch = ''">Browse matches</button></div>
        </div></div>

      </template>
      <template v-else-if="page === 'Communities'">
        <div class="section-heading community-heading"><button ref="createButton" type="button" class="create-group-button" aria-label="Create community" @click="openCreateGroup">+</button></div><div class="community-list"><button v-for="group in groups" :key="group.id" type="button" class="community-row community-row-button" @click="openGroup(group)"><span><strong>{{ group.name }}</strong><small>{{ group.sample ? 'Sample community' : 'Your preview community' }}</small></span><span class="match-chevron" aria-hidden="true">&#8250;</span></button></div>

      </template>
      <template v-else>
        <div class="section-toolbar"><label class="scope-label">Leaderboard<select v-model="scope"><option>Global</option><option v-for="group in groups" :key="group.id" :value="group.name">{{ group.name }}</option></select></label></div><p class="ranking-caption">{{ scope }} · Season preview</p><ol class="ranking-list"><li v-for="(person, index) in ['Pavol K.', 'Tondo M.', 'Matúš N.', name]" :key="index" :class="{ 'your-rank': index === 3 }"><span class="rank-position">{{ index + 1 }}</span><span>{{ person }} <small v-if="index === 3">You · sample position</small></span><strong>{{ [128, 116, 104, 92][index] }} <span>pts</span></strong></li></ol><p class="quiet ranking-caption">Sample standings.</p>
      </template>
      
    </div>
    <section v-else-if="selected" class="match-detail" aria-labelledby="detail-title">
      <button type="button" class="detail-back" aria-label="Back to matches" @click="closeMatch"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5m0 0 6-6m-6 6 6 6"/></svg></button>
      <div class="fixture-heading">
        <p>{{ selected.league }} <span aria-hidden="true">&#183;</span> {{ time(selected) }}</p>
        <h1 id="detail-title" ref="detailHeading" tabindex="-1">{{ selected.home }} <span>vs</span> {{ selected.away }}</h1>
        <p>{{ selected.venue }}</p><button class="text-button" type="button" @click="extraScreen = 'event'">Matchday details</button>
      </div>
      <section class="prediction-section" aria-labelledby="prediction-title">
        <div class="detail-section-heading"><h2 id="prediction-title">Your prediction</h2><span v-if="selected.start <= now" class="quiet">Closed</span></div>
        <template v-if="selected.start <= now">
          <p class="result-preview">Sample result: 2 : 1</p>
          <p v-if="picks[selected.id]" class="closed-pick">{{ picks[selected.id]?.home }} : {{ picks[selected.id]?.away }}</p>
          <p v-else class="quiet">Predictions closed at kickoff.</p>
        </template>
        <form v-else class="prediction-form" @submit.prevent="save">
          <p v-if="notice" class="notice" role="status">{{ notice }}</p>
          <div class="score-inputs">
            <div class="score-team"><label for="home-score">{{ selected.home }}</label><div class="score-card"><input id="home-score" v-model="home" type="number" inputmode="numeric" min="0" max="99" step="1" required placeholder="–"><div class="score-controls"><button type="button" :aria-label="`Decrease ${selected.home} score`" :disabled="home === '' || Number(home) <= 0" @click="adjustScore('home', -1)">−</button><button type="button" :aria-label="`Increase ${selected.home} score`" :disabled="Number(home) >= 99 && home !== ''" @click="adjustScore('home', 1)">+</button></div></div></div>
            <span aria-hidden="true">:</span>
            <div class="score-team"><label for="away-score">{{ selected.away }}</label><div class="score-card"><input id="away-score" v-model="away" type="number" inputmode="numeric" min="0" max="99" step="1" required placeholder="–"><div class="score-controls"><button type="button" :aria-label="`Decrease ${selected.away} score`" :disabled="away === '' || Number(away) <= 0" @click="adjustScore('away', -1)">−</button><button type="button" :aria-label="`Increase ${selected.away} score`" :disabled="Number(away) >= 99 && away !== ''" @click="adjustScore('away', 1)">+</button></div></div></div>
          </div>
          <p class="prediction-help">Final score. Edit any time before kickoff. <button type="button" class="inline-link" @click="extraScreen = 'rules'">Scoring</button></p>
          <button class="primary" :disabled="!valid || selected.start <= now">{{ picks[selected.id] ? 'Save changes' : 'Save prediction' }}</button>
        </form>
      </section>
      <section class="friends-section" aria-labelledby="community-picks-title">
        <div class="detail-section-heading"><h2 id="community-picks-title">Community bets</h2><span class="quiet">Preview</span></div>
        
        <label class="community-select">Community<select v-model="matchGroupId"><option v-for="group in groups" :key="group.id" :value="group.id">{{ group.name }}</option></select></label>
        <p v-if="!groups.length" class="group-empty">Join or create a group to see bets.</p>
        <p v-else-if="!matchCommunityPicks.length" class="group-empty">No member predictions yet.</p>
        <ul v-else class="friend-list"><li v-for="member in matchCommunityPicks" :key="member.name">
          <span class="friend-avatar" aria-hidden="true">{{ member.name.slice(0, 1) }}</span>
          <span class="friend-name">{{ member.name }}</span><strong class="friend-score">{{ member.home }} : {{ member.away }}</strong>
          <div v-if="matchGroupId !== null" class="reaction-buttons" :aria-label="`React to ${member.name}'s prediction`" role="group">
            <button v-for="reaction in (['like', 'dislike'] as const)" :key="reaction" type="button" class="reaction" :class="[reaction, { reacted: reactions[reactionKey(matchGroupId, selected.id, member.name)] === reaction }]" :aria-pressed="reactions[reactionKey(matchGroupId, selected.id, member.name)] === reaction" :aria-label="`${reaction === 'like' ? 'Like' : 'Dislike'} ${member.name}'s prediction`" @click="toggleReaction(matchGroupId, selected.id, member.name, reaction)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" :class="{ 'thumb-down': reaction === 'dislike' }"><path d="M7 10v11H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3Zm0 0 4-7a2 2 0 0 1 2-1c1.1 0 1.6 1 1.3 2L13 8h5.5a3 3 0 0 1 2.9 3.7l-1.6 7A3 3 0 0 1 16.9 21H7" /></svg>
            </button>
          </div>
        </li></ul>
        <p class="sample-note">Member bets and reactions are preview data.</p>
      </section>
    </section>
    <section v-else-if="selectedGroup" class="group-detail" aria-labelledby="group-title">
      <button type="button" class="detail-back" aria-label="Back to groups" @click="closeGroup"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5m0 0 6-6m-6 6 6 6"/></svg></button>
      <div class="group-intro"><h1 id="group-title" ref="groupHeading" tabindex="-1">{{ selectedGroup.name }}</h1><p>{{ selectedGroup.sample ? 'Sample community' : 'Your preview community' }}</p></div>
      <div class="group-actions"><button type="button" @click="extraScreen = 'competitions'">Competitions</button><button type="button" @click="extraScreen = 'group-settings'">Settings</button></div>
      <div class="group-tabs" role="group" aria-label="Community sections"><button v-for="item in (['Members', 'Rankings', 'Bets'] as const)" :key="item" :aria-pressed="groupTab === item" :class="{ active: groupTab === item }" @click="groupTab = item; notice = ''">{{ item }}</button></div>
      <section v-if="groupTab === 'Members'" class="group-panel">
        <div class="detail-section-heading"><h2>Members</h2><button type="button" class="text-button" @click="inviteOpen = !inviteOpen" :aria-expanded="inviteOpen">{{ inviteOpen ? 'Close' : 'Invite friends' }}</button></div>
        <p v-if="notice" class="notice" role="status">{{ notice }}</p>
        <form v-if="inviteOpen" class="invite-form" @submit.prevent="addPreviewMember"><label for="invite-name">Friend's name</label><div class="invite-row"><input id="invite-name" v-model="inviteName" maxlength="60" required placeholder="Enter a name"><button class="pick-button" :disabled="!inviteName.trim()">Add</button></div><p class="sample-note">Preview only. No invitation will be sent.</p></form>
        <ul class="member-list"><li><span class="friend-avatar">{{ name.trim().slice(0, 1).toUpperCase() }}</span><span>{{ name }} <small>You</small></span></li><li v-for="member in (sampleMembers[selectedGroup.id] ?? [])" :key="member"><span class="friend-avatar">{{ member.slice(0, 1) }}</span><span>{{ member }} <small>Sample</small></span></li><li v-for="(invited, index) in selectedGroup.invited" :key="index"><span class="friend-avatar">{{ invited.slice(0, 1).toUpperCase() }}</span><span>{{ invited }} <small>Preview only</small></span></li></ul>
        <p v-if="!selectedGroup.sample && !selectedGroup.invited.length" class="group-empty">Invite friends to start your community.</p>
      </section>
      <section v-else-if="groupTab === 'Rankings'" class="group-panel"><h2>Rankings</h2><template v-if="selectedGroup.sample"><p class="sample-note">Sample standings</p><ol class="group-rank-list"><li v-for="(member, index) in (sampleMembers[selectedGroup.id] ?? [])" :key="member"><span>{{ index + 1 }}. {{ member }}</span><strong>{{ [128, 116, 104][index] }} pts</strong></li></ol></template><p v-else class="group-empty">Rankings will appear when results are available.</p></section>
      <section v-else class="group-panel" aria-labelledby="group-picks-title">
        <h2 id="group-picks-title">Predictions</h2>
        <label class="group-match-select">Match<select v-model="groupMatchId"><option v-for="match in matches" :key="match.id" :value="match.id">{{ match.home }} vs {{ match.away }}</option></select></label>
        <p v-if="groupMatch" class="sample-note">{{ time(groupMatch) }} &#183; {{ groupMatch.league }}</p>
        <ul v-if="selectedGroupPicks.length || picks[groupMatchId]" class="group-rank-list">
          <li v-if="picks[groupMatchId]"><span>You</span><strong>{{ picks[groupMatchId]?.home }} : {{ picks[groupMatchId]?.away }}</strong></li>
          <li v-for="member in selectedGroupPicks" :key="member.name"><span>{{ member.name }} <small>Sample member</small></span><strong>{{ member.home }} : {{ member.away }}</strong></li>
        </ul>
        <p v-if="!selectedGroupPicks.length" class="group-empty">No member predictions yet.</p>
        <button v-if="groupMatch" type="button" class="text-button" @click="open(groupMatch, selectedGroup.id)">{{ picks[groupMatchId] ? 'View your prediction' : 'Open match' }}</button>
        <p class="sample-note">Member predictions are sample data.</p>
      </section>
    </section>
    <section v-else-if="creatingGroup" class="community-create" aria-labelledby="create-community-title">
      <button type="button" class="detail-back" aria-label="Back to groups" @click="closeCreateGroup"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5m0 0 6-6m-6 6 6 6"/></svg></button>
      <div class="create-intro"><h1 id="create-community-title" ref="createHeading" tabindex="-1">New community</h1></div>
      <form class="community-form" @submit.prevent="createGroup">
        <label for="group-name">Community name</label>
        <input id="group-name" v-model="groupName" required maxlength="60" placeholder="e.g. The Sunday regulars">
        <p class="create-help">Preview only. Groups reset on reload; invitations are not sent.</p>
        <button class="primary" :disabled="!groupName.trim()">Create community</button>
      </form>
    </section>
    <section v-else class="profile-screen" aria-labelledby="profile-title">
      <button type="button" class="detail-back" aria-label="Back to workspace" @click="closeProfile"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5m0 0 6-6m-6 6 6 6"/></svg></button>
      <div class="create-intro"><h1 id="profile-title" ref="profileHeading" tabindex="-1">Profile</h1></div>
      <div class="profile-details">
        <div class="profile-identity"><span class="profile-avatar" aria-hidden="true">{{ name.trim().slice(0, 1).toUpperCase() }}</span><div><h2>{{ name }}</h2><p>{{ email }}</p></div></div>
        <div class="profile-stats" aria-label="Your statistics"><div><strong>{{ Object.keys(picks).length }}</strong><span>Predictions</span></div><div><strong>&#8212;</strong><span>Correct</span></div><div><strong>&#8212;</strong><span>Rank</span></div></div><p class="stats-note">Results and rankings are not connected yet.</p>
        <div class="profile-links"><button type="button" @click="extraScreen = 'rules'">Scoring rules <span aria-hidden="true">&#8250;</span></button><button type="button" @click="extraScreen = 'admin'">Administration preview <span aria-hidden="true">&#8250;</span></button></div><button type="button" class="profile-signout" :disabled="busy" @click="$emit('logout')">{{ busy ? 'Signing out...' : 'Sign out' }}</button>
      </div>
      <p class="profile-preview">Preview: sample matches, community members and rankings. Bets, reactions and communities reset on reload.</p>
    </section>

  </div>
</template>
