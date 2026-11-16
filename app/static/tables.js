const filter=document.getElementById('filter');
filter?.addEventListener('input',()=>{const value=filter.value.trim().toLowerCase();document.querySelectorAll('#evidence-table tbody tr').forEach(row=>row.hidden=!row.textContent.toLowerCase().includes(value));});
