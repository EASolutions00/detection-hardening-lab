using System;

// TeLoS capture-window fence.
// Purpose: create exactly one process, so Sysmon records exactly one Event ID 1
// whose CommandLine uniquely identifies one boundary of one capture window.
// It does nothing else on purpose. Any extra work would emit extra events.
public class TelosFence
{
    public static int Main(string[] args)
    {
        string tag = (args.Length > 0) ? args[0] : "NOTAG";
        string runId = (args.Length > 1) ? args[1] : "NORUN";
        Console.WriteLine("TELOS-FENCE " + tag + " " + runId + " " +
                          DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ"));
        return 0;
    }
}
