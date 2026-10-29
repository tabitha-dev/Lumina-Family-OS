"use strict";
/* Small progressive enhancements for the existing vanilla-JS family dashboard. */
function localDateKey(input){
 const d=input instanceof Date?input:new Date(input);
 return [d.getFullYear(),String(d.getMonth()+1).padStart(2,"0"),String(d.getDate()).padStart(2,"0")].join("-");
}
function toggleMobileMore(force){
 const panel=document.getElementById("luminaMoreMenu"),button=document.getElementById("luminaMoreButton");
 if(!panel||!button)return;
 const open=typeof force==="boolean"?force:panel.hidden;
 panel.hidden=!open;
 button.setAttribute("aria-expanded",String(open));
 if(open)panel.querySelector("button")?.focus();
}
function renderLuminaToday(){
 const tasks=(data.tasks||[]).filter(t=>t.type==="routine");
 const done=tasks.filter(t=>t.done).length;
 const today=localDateKey(new Date());
 const events=(data.events||[]).filter(e=>e.date===today).length;
 const shopping=(data.list||[]).filter(i=>!i.checked).length;
 const put=(id,value)=>{const el=document.getElementById(id);if(el)el.textContent=String(value);};
 put("luminaRoutinesDone",done+" / "+tasks.length);
 put("luminaEventsToday",events);
 put("luminaShoppingCount",shopping);
}
function enhanceKeyboardTargets(){
 document.querySelectorAll(".task-card,.month-cell[onclick],.event-block[onclick]").forEach(el=>{
  el.setAttribute("role","button");
  el.setAttribute("tabindex","0");
  if(el.classList.contains("task-card"))el.setAttribute("aria-pressed",el.classList.contains("completed")?"true":"false");
  if(el.dataset.keyboardBound)return;
  el.dataset.keyboardBound="true";
  el.addEventListener("keydown",event=>{
   if(event.key==="Enter"||event.key===" "){event.preventDefault();el.click();}
  });
 });
}
function downloadFamilyBackup(){
 try{
  const backup={format:"lumina-family-os",version:1,exportedAt:new Date().toISOString(),data:JSON.parse(JSON.stringify(data))};
  const blob=new Blob([JSON.stringify(backup,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob);
  const link=document.createElement("a");
  link.href=url;link.download="lumina-family-backup-"+localDateKey(new Date())+".json";
  document.body.appendChild(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  const status=document.getElementById("luminaNotice");
  if(status)status.textContent="Backup downloaded to your device.";
 }catch(error){alert("Unable to create a backup in this browser.");}
}
async function restoreFamilyBackup(event){
 const input=event.target,file=input.files?.[0];if(!file)return;
 try{
  if(file.size>5*1024*1024)throw Error("Backup file is too large.");
  const archive=JSON.parse(await file.text());
  if(archive?.format!=="lumina-family-os"||archive.version!==1||!archive.data)throw Error("This file is not a Lumina backup.");
  const candidate=archive.data;
  const arrays=["profiles","tasks","events","meals","list","pantry","wellness","rewards"];
  if(!arrays.every(k=>Array.isArray(candidate[k]))||!candidate.settings||typeof candidate.settings!=="object")throw Error("Backup is incomplete.");
  if(!confirm("Restore this backup? It will replace all family data in this browser. Download a backup of the current data first."))return;
  localStorage.setItem(DB,JSON.stringify(candidate));
  location.reload();
 }catch(error){alert(error?.message||"Could not restore this backup.");}
 finally{input.value="";}
}
document.addEventListener("keydown",event=>{
 if(event.key==="Escape")toggleMobileMore(false);
});
document.addEventListener("click",event=>{
 const panel=document.getElementById("luminaMoreMenu"),button=document.getElementById("luminaMoreButton");
 if(panel&&!panel.hidden&&!panel.contains(event.target)&&!button?.contains(event.target))toggleMobileMore(false);
});
