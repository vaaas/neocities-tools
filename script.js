L=location
D=document
B='attributes'
C='classList'
q='querySelector'
Q=q+'All'
A='active'
M=x=>F(x.target[B].href.value)
F=T=>{for(x of D[Q]('article'))x[C][T=='all'||x[B].t.value==T?'remove':'add']('hide')
if(x=D[q]('a.'+A))x[C].remove(A)
if(x=D[q](`a[href="${T}"]`))x[C].add(A)
history.pushState(null,D.title,L.origin+L.pathname+'?'+T)
return !1}
for(x of D[Q]('#cats a'))x.onclick=M
L.search.length>1&&F(L.search.slice(1))
