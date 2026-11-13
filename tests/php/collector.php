<?php
declare(strict_types=1);
require (is_dir(__DIR__.'/../../collector') ? __DIR__.'/../../collector' : __DIR__.'/../../server/analytics').'/Collector.php';
use LeadAnalytics\Collector;
function check(bool $ok,string $why):void {if(!$ok)throw new RuntimeException($why);}
function event(int $i,string $kind='access',string $item='dbs'):array {
 return ['schema'=>1,'event_id'=>sprintf('12345678-1234-4234-8234-%012d',$i),'kind'=>$kind,'item'=>$item,
         'app_version'=>'3.2.1','runtime_version'=>'R2024b','outcome'=>$kind==='access'?'request':'redirect','consent'=>true];
}
$dir=sys_get_temp_dir().'/lead-collector-'.bin2hex(random_bytes(8));mkdir($dir,0700);$path=$dir.'/events.sqlite';
try {
 $mask=umask();
 $collector=new Collector($path,random_bytes(32),fn($ip)=>'DE');
 check(umask()===$mask,'constructor restores process umask');
 check((fileperms($path)&0777)===0600,'database private mode');
 $now=new DateTimeImmutable('2026-01-02T12:00:00Z');
 check($collector->record(event(1),'192.0.2.1','MATLAB',$now)==='accepted','accept event');
 check($collector->record(event(1),'192.0.2.1','MATLAB',$now)==='duplicate','idempotent event');
 $collector->record(event(2),'192.0.2.1','MATLAB',$now);
 $collector->record(event(3,'access','group'),'192.0.2.1','MATLAB',$now);
 $collector->record(event(4,'download','latest'),'192.0.2.1','MATLAB',$now);
 $collector->record(event(5,'download','latest'),'192.0.2.1','SomeBot',$now);
 $bad=event(6,'download','latest');$bad['outcome']='not_found';
 $collector->record($bad,'192.0.2.2','Browser',$now);
 $collector->record(event(7,'download','latest'),'192.0.2.3','SomeBot',$now);
 $export=$collector->aggregate('2026-01-02');
 check($export['series']['access'][0]['n']===1,'address/hour dedup');
 check(count($export['series']['tools'])===2,'tool counts independent');
 check(array_sum(array_column($export['series']['download_requests'],'n'))===1,'response requests deduped; failures and declared automation excluded');
 check(count($export['series']['outcomes'])===4,'outcomes retain failure and automation diagnostics');
 foreach(['patient','filename','path','ip'] as $field) {
  try {Collector::validate(event(9)+[$field=>'forbidden']);throw new RuntimeException('accepted extra field');}
  catch(InvalidArgumentException $e) {}
 }
 foreach([false,null,'true'] as $consent) {
  $bad=event(9);$bad['consent']=$consent;
  try {Collector::validate($bad);throw new RuntimeException('accepted non-opted-in client');}
  catch(InvalidArgumentException $e) {}
 }
 $bad=event(9);$bad['item']='patient_name';
 try {Collector::validate($bad);throw new RuntimeException('accepted arbitrary tool');}catch(InvalidArgumentException $e){}
 for($i=10;$i<80;$i++)$result=$collector->record(event($i),'192.0.2.1','MATLAB',$now);
 check($result==='rate_limited','bounded per-minute requests');
 $collector->record(event(100),'192.0.2.1','MATLAB',$now->modify('+1 day'));
 $db=new PDO('sqlite:'.$path);
 $tokens=$db->query('SELECT DISTINCT subject FROM events')->fetchAll(PDO::FETCH_COLUMN);
 check(count($tokens)===4,'daily identity rotates');
 check(!str_contains(file_get_contents($path),'192.0.2.1'),'raw address not stored');
 check(!str_contains(json_encode($export),'subject'),'export has no token');
 $retained=$collector->retain(new DateTimeImmutable('2026-03-01T00:00:00Z'));
 check($retained['events']>0 && $collector->health()['events_retained']===0,'retention enforced');
 echo "Collector validation, consent, idempotency, deduplication, rates, privacy and retention passed.\n";
} finally {foreach(glob($dir.'/*')as$f)unlink($f);rmdir($dir);}
