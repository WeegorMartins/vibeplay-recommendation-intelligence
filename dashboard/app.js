const fmtInt = new Intl.NumberFormat('pt-BR');
const pct = value => `${(value * 100).toFixed(1).replace('.', ',')}%`;
const plotConfig = {displayModeBar:false,responsive:true};
const colors = {green:'#46f09b',green2:'#a8ffd1',muted:'#91a9a0',grid:'#20352f',paper:'rgba(0,0,0,0)'};
let state = {data:null,recommendations:[]};

function layout(extra={}){return {paper_bgcolor:colors.paper,plot_bgcolor:colors.paper,font:{family:'DM Sans',color:colors.muted,size:11},margin:{l:44,r:12,t:18,b:40},xaxis:{gridcolor:colors.grid,zeroline:false},yaxis:{gridcolor:colors.grid,zeroline:false},...extra}}

async function loadData(){
  const response = await fetch('assets/dashboard_data.json');
  if(!response.ok) throw new Error('Não foi possível carregar dashboard_data.json');
  const data = await response.json(); state.data=data; state.recommendations=data.recommendations;
  render(data);
}

function render(data){
  document.querySelector('#updatedAt').textContent = new Date(data.generated_at).toLocaleString('pt-BR');
  document.querySelector('#kpiUsers').textContent = fmtInt.format(data.kpis.users);
  document.querySelector('#kpiInteractions').textContent = fmtInt.format(data.kpis.interactions);
  document.querySelector('#kpiRecall').textContent = pct(data.kpis.recall_at_10);
  document.querySelector('#kpiCoverage').textContent = pct(data.kpis.coverage);
  document.querySelector('#metricPrecision').textContent = pct(data.metric_cards.precision_at_10);
  document.querySelector('#metricNdcg').textContent = pct(data.metric_cards.ndcg_at_10);
  document.querySelector('#metricNovelty').textContent = data.metric_cards.novelty.toFixed(2);

  Plotly.newPlot('dailyChart',[{x:data.daily.map(x=>x.date),y:data.daily.map(x=>x.events),type:'scatter',mode:'lines',line:{color:colors.green,width:2},fill:'tozeroy',fillcolor:'rgba(70,240,155,.08)',hovertemplate:'%{x}<br><b>%{y}</b> eventos<extra></extra>'}],layout({margin:{l:38,r:8,t:18,b:35}}),plotConfig);
  Plotly.newPlot('funnelChart',[{labels:data.event_funnel.map(x=>x.event),values:data.event_funnel.map(x=>x.value),type:'pie',hole:.72,marker:{colors:['#46f09b','#23b779','#9cffe0','#48655c']},textinfo:'percent',hovertemplate:'%{label}: %{value:,}<extra></extra>'}],layout({showlegend:true,legend:{orientation:'h',y:-.08},annotations:[{text:'eventos',showarrow:false,font:{size:12,color:colors.muted}}]}),plotConfig);
  const metrics=[['precision_at_10','Precisão@10'],['recall_at_10','Recall@10'],['ndcg_at_10','NDCG@10']];
  Plotly.newPlot('modelChart',data.model_comparison.map((model,i)=>({x:metrics.map(x=>x[1]),y:metrics.map(x=>model[x[0]]),name:model.model,type:'bar',marker:{color:i?colors.green:'#49675e'},hovertemplate:'%{x}: <b>%{y:.1%}</b><extra>'+model.model+'</extra>'})),layout({barmode:'group',yaxis:{tickformat:'.0%',gridcolor:colors.grid,range:[0,Math.max(...data.model_comparison.flatMap(m=>metrics.map(x=>m[x[0]])))*1.25]},legend:{orientation:'h',y:1.12}}),plotConfig);
  const genre=data.catalog_genres.slice().reverse();
  Plotly.newPlot('genreChart',[{x:genre.map(x=>x.titles),y:genre.map(x=>x.genre),type:'bar',orientation:'h',marker:{color:genre.map((_,i)=>`rgba(70,240,155,${.35+i/genre.length*.6})`)},hovertemplate:'%{y}: <b>%{x}</b> títulos<extra></extra>'}],layout({margin:{l:120,r:15,t:10,b:35}}),plotConfig);
  renderRecommendations(); renderGovernance(data.governance); renderRegions(data.regions);
}

function renderRecommendations(){
  const term=document.querySelector('#titleSearch').value.toLowerCase(); const type=document.querySelector('#typeFilter').value; const sort=document.querySelector('#sortFilter').value;
  let rows=state.recommendations.filter(x=>(type==='Todos'||x.type===type)&&(`${x.title} ${x.genres}`.toLowerCase().includes(term)));
  rows.sort((a,b)=>sort==='score'?b.score-a.score:sort==='year'?b.release_year-a.release_year:a.rank-b.rank);
  const palette=['#46f09b','#67d5ff','#b595ff','#ffd166','#ff8fa3'];
  document.querySelector('#recommendationGrid').innerHTML=rows.map((x,i)=>`<article class="rec-card" style="--card-accent:${palette[i%palette.length]}"><span class="rank">#${String(x.rank).padStart(2,'0')}</span><h3>${escapeHtml(x.title)}</h3><div class="meta">${x.type} · ${x.release_year} · nota ${Number(x.quality_score).toFixed(1)}</div><div class="genres">${x.genres.split('|').map(g=>`<span>${escapeHtml(g)}</span>`).join('')}</div><div class="reason">${escapeHtml(x.reason)}</div><span class="score">score ${Number(x.score).toFixed(3)}</span></article>`).join('') || '<p>Nenhum título encontrado.</p>';
}

function renderGovernance(rows){document.querySelector('#governanceGrid').innerHTML=rows.map(x=>`<article class="governance-card"><header><strong>${escapeHtml(x.check)}</strong><span class="health">● ${escapeHtml(x.status)}</span></header><div class="gauge"><i style="width:${Math.min(x.value*100,100)}%"></i></div><footer><span>Atual ${pct(x.value)}</span><span>Limite ${pct(x.threshold)}</span></footer></article>`).join('')}
function renderRegions(rows){document.querySelector('#regionTable').innerHTML=`<table class="region-table"><thead><tr><th>REGIÃO</th><th>USUÁRIOS</th><th>INTERAÇÕES</th><th>WATCH MÉDIO</th></tr></thead><tbody>${rows.map(x=>`<tr><td>${x.region}</td><td>${fmtInt.format(x.users)}</td><td>${fmtInt.format(x.interactions)}</td><td>${pct(x.avg_watch)}</td></tr>`).join('')}</tbody></table>`}
function escapeHtml(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}

function botAnswer(question){
  const q=question.toLowerCase(), d=state.data, m=d.metric_cards;
  if(/recall|acerto|encontr/.test(q)) return [`O Recall@10 é ${pct(m.recall_at_10)}. Ele mede quanto dos itens relevantes do teste apareceu nas dez primeiras posições.`,`É evidência offline; ainda precisamos do A/B test para afirmar impacto de negócio.`];
  if(/cobertura|catálogo|catalogo/.test(q)) return [`A cobertura chegou a ${pct(m.catalog_coverage)}, reduzindo a dependência dos títulos mais populares.`,`Eu acompanharia esse indicador também por gênero e região.`];
  if(/divers|bolha|repet/.test(q)) return [`A diversidade média é ${pct(m.genre_diversity)}. O re-ranking MMR troca um pouco de score bruto por variedade.`,`Vale testar lambdas de 0,70 a 0,85 no experimento.`];
  if(/cold|novo|sem hist/.test(q)) return [`Para novos usuários, usamos 3 preferências declaradas + popularidade qualificada + frescor. O comportamento passa a pesar conforme surgem interações.`,`Isso evita uma home vazia sem fingir que já conhecemos a pessoa.`];
  if(/negócio|negocio|a\/b|validar|resultado/.test(q)) return [`O A/B test deve ter horas assistidas por usuário como métrica primária; CTR, conclusão e retenção D30 como secundárias.`,`Skips, latência e concentração do catálogo funcionam como guardrails.`];
  if(/por que|explic|recomend/.test(q)) return [`Cada card mostra um motivo: afinidade com consumo positivo, gênero preferido ou padrão de pessoas semelhantes.`,`Explicação é parte do produto, não apenas do relatório técnico.`];
  return [`Posso explicar Recall@10, cobertura, diversidade, cold start, explicabilidade ou o teste A/B.`,`Tente: “Como validar o resultado no negócio?”`];
}

document.querySelectorAll('#titleSearch,#typeFilter,#sortFilter').forEach(el=>el.addEventListener('input',renderRecommendations));
document.querySelector('#themeButton').addEventListener('click',()=>document.body.classList.toggle('light'));
const drawer=document.querySelector('#chatDrawer'), body=document.querySelector('#chatBody'), input=document.querySelector('#chatInput');
document.querySelector('#chatLauncher').addEventListener('click',()=>{drawer.classList.add('open');input.focus()});
document.querySelector('#chatClose').addEventListener('click',()=>drawer.classList.remove('open'));
function ask(question){if(!question.trim())return;body.insertAdjacentHTML('beforeend',`<div class="message user">${escapeHtml(question)}</div>`);const [answer,next]=botAnswer(question);setTimeout(()=>{body.insertAdjacentHTML('beforeend',`<div class="message bot">${answer}<small>${next}</small></div>`);body.scrollTop=body.scrollHeight},180);body.scrollTop=body.scrollHeight}
document.querySelector('#chatForm').addEventListener('submit',e=>{e.preventDefault();ask(input.value);input.value=''})
document.querySelectorAll('.suggestions button').forEach(b=>b.addEventListener('click',()=>ask(b.textContent)));
const sections=[...document.querySelectorAll('.section-block')], links=[...document.querySelectorAll('.nav-item')];new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.toggle('active',l.getAttribute('href')===`#${e.target.id}`))}}),{threshold:.25}).observe && sections.forEach(s=>new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting)links.forEach(l=>l.classList.toggle('active',l.getAttribute('href')===`#${e.target.id}`))}),{threshold:.25}).observe(s));
loadData().catch(err=>{document.querySelector('main').insertAdjacentHTML('afterbegin',`<p style="padding:12px;background:#5c2525">${escapeHtml(err.message)}. Abra via servidor HTTP conforme o README.</p>`) });
