import java.util.*; 
import java.io.*;
import java.nio.file.*;
import java.io.PrintWriter;

public class kcluster
{
	
	public static void main(String[] args){
		String InputFile="";
		String Criterion;
		String ClassFile;
		int k;
		int TrialCount;
		String OutputFile;
		Map<String, Map<Integer,Float>> Articles=new HashMap<String, Map<Integer,Float>>();
		Map<Integer,String> ArticleIndexMap=new HashMap<Integer,String>();

		int[] seeds=new int[]{1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39};

		long startTime = System.currentTimeMillis();

		if(args.length==6){
			InputFile=args[0];
			Criterion=args[1];
			ClassFile=args[2];
			k=Integer.parseInt(args[3]);
			TrialCount=Integer.parseInt(args[4]);
			OutputFile=args[5];

			try{
			String data = new String(Files.readAllBytes(Paths.get(InputFile)));
			String[] lines=data.split("\n"); 
			String CurrentArticle=lines[0].split(",")[0];
			Map<Integer,Float> FrequencyVector= new HashMap<Integer,Float>();
			int temp =0;
			for(String art:lines ){
				// System.out.println(art);
				// if(temp++>3)
				// 	break;
				String[] DocFreq=art.split(",");
				if(DocFreq[0].equals(CurrentArticle)){
					FrequencyVector.put(Integer.valueOf(DocFreq[1]),Float.valueOf(DocFreq[2]));
				}
				else{
					Articles.put(CurrentArticle,FrequencyVector);
					CurrentArticle=DocFreq[0];
					FrequencyVector = new HashMap<Integer,Float>();
					FrequencyVector.put(Integer.valueOf(DocFreq[1]),Float.valueOf(DocFreq[2]));
				}
			}
			Articles.put(CurrentArticle,FrequencyVector);
			
			
			int count=0;
			for(Map.Entry<String, Map<Integer,Float>> entry : Articles.entrySet()){
				ArticleIndexMap.put(count,entry.getKey());
				count++;
			}

			float minSSE=999999;
			float maxSimilarity=0;
			Map<String,Integer> BestClusterMapping =new HashMap<String, Integer>();


			for(int i=0;i<TrialCount;i++){
				float SSE=0;
				float Similarity=0;
				//seed with random initial centroids
				ArrayList<Integer> RandomPointIDList=new ArrayList<Integer>();
				Map<Integer,float[]> Centroids= new HashMap<Integer,float[]>();	
				ArrayList<Map<String,Integer>> PointMappingArray =new ArrayList<Map<String,Integer>>();
				ArrayList<Float> SSEList=new ArrayList<Float>();

				Random rand=new Random(seeds[i]);
				for(int j=0;j<k;j++){
					int RandIndex=rand.nextInt(ArticleIndexMap.size());
					if(RandomPointIDList.contains(RandIndex))
						j--;
					RandomPointIDList.add(RandIndex);
				}
				int clusterNo=0;
				for(int index: RandomPointIDList){
					String newId=ArticleIndexMap.get(index);
					float[] tempCoord=new float[5618];
					Map<Integer,Float> ActualCoord=new HashMap<Integer,Float>();
					ActualCoord=Articles.get(newId);
					for(Map.Entry<Integer,Float> entry : ActualCoord.entrySet()){
						tempCoord[entry.getKey()]=entry.getValue();
					}	
					Centroids.put(clusterNo,tempCoord);	
					clusterNo++;
				}
				
				Map<String,Integer> PointClusterMapping =new HashMap<String, Integer>();
				Map<String,Integer> NewPointClusterMapping =new HashMap<String, Integer>();

				PointClusterMapping=AssignPoints(Articles,k,Centroids,Criterion);
				// Map<String,Integer> OldMapping=new HashMap<String,Integer>();
				// OldMapping=CopyPointMapping(PointClusterMapping);
				// PointMappingArray.add(OldMapping);


				
				for(Map.Entry<String,Integer> entry: PointClusterMapping.entrySet()){
					//System.out.println(entry.getKey()+" "+entry.getValue());
				}
				
				Map<Integer,float[]> NewCentroids=new HashMap<Integer,float[]>();
				if(Criterion.toLowerCase().equals("sse")){
					SSE=ComputeSSE(PointClusterMapping,Centroids,Articles);
					SSEList.add(SSE);
					// System.out.println(SSE);
				}
				else if(Criterion.toLowerCase().equals("i2")){
					Similarity=ComputeGlobalCosine(PointClusterMapping,Centroids,Articles);

				}

				NewCentroids= RecomputeCentroids(Articles,PointClusterMapping,k);

				int trial=0;

				do{
					Centroids=NewCentroids;
					if(NewPointClusterMapping.size()!=0)
						PointClusterMapping=CopyPointMapping(NewPointClusterMapping);
					NewPointClusterMapping=AssignPoints(Articles,k,Centroids,Criterion);
					if(Criterion.toLowerCase().equals("sse")){
						SSE=ComputeSSE(NewPointClusterMapping,Centroids,Articles);
						// System.out.println(SSE);
						if(SSE<minSSE){
							minSSE=SSE;
							BestClusterMapping=CopyPointMapping(NewPointClusterMapping);
						}	
					}
					if(Criterion.toLowerCase().equals("i2")){
						Similarity=ComputeGlobalCosine(PointClusterMapping,Centroids,Articles);
						//System.out.println(Similarity);
						if(Similarity>maxSimilarity){
							maxSimilarity=Similarity;
							BestClusterMapping=CopyPointMapping(NewPointClusterMapping);
						}	
					}
					NewCentroids= RecomputeCentroids(Articles,NewPointClusterMapping,k);	
					trial++;
				}
				while(ComparePointMappinngs(PointClusterMapping,NewPointClusterMapping)==false);
				System.out.println("\nCONVERGED\n");

				//ComputeEntropy(ClassFile,PointClusterMapping,k);
				//Centroids= new HashMap<Integer,float[]>();
			}

			ComputeEntropy(ClassFile,BestClusterMapping,k);
			
			long endTime = System.currentTimeMillis();

			// if(Criterion.toLowerCase().equals("i2")){
			// 	System.out.println("Criterion function value : "+minSSE);
			// }

			// if(Criterion.toLowerCase().equals("sse")){
			// 	System.out.println("Criterion function value : "+maxSimilarity);
			// }
			System.out.println("Execution time: " + (endTime - startTime)/1000 + " seconds");

			//write output file
			PrintWriter pw = new PrintWriter(new File(OutputFile));
			StringBuffer csv = new StringBuffer("");
            
			for(String key:BestClusterMapping.keySet()){
				csv.append(key);
				csv.append(',');
				csv.append(BestClusterMapping.get(key));
				csv.append('\n');

			}

            pw.write(csv.toString());
            pw.close();


		}
		catch(Exception e){
			System.out.println(e);
		}
		
		}
		else{
			System.out.println("Please enter all arguments");
		}

		
		
	}

	
	static Map<String,Integer> AssignPoints(Map<String, Map<Integer,Float>> Articles,int k, Map<Integer,float[]> Centroids, String Criteria ){
		Map<String,Integer> PointClusterMapping =new HashMap<String, Integer>();
		//Assign points to clusters
		//System.out.println(Articles.size());
		for (Map.Entry<String, Map<Integer,Float>> entry : Articles.entrySet()) {
		    float minDist=99999999;
			for(int j=0;j<k;j++){
				
				if(Criteria.toLowerCase().equals("sse")){
					// System.out.println(""+entry.getValue()+"::"+Centroids.get(j).toString());
					float dist=CalculateEuclideanDistance(entry.getValue(),Centroids.get(j));
					//System.out.println(dist);
					if(dist!=0){
						if(j==0 || dist<minDist){
						//System.out.println(minDist+" "+ j);
						minDist=dist;
						PointClusterMapping.put(entry.getKey(),j);
						}
					}
					
					
				}
				if(Criteria.toLowerCase().equals("i2")){
					float dist=CalculateCosineSimilarity(entry.getValue(),Centroids.get(j));
					if(dist!=1){
						if(j==0 || dist>minDist){
						minDist=dist;
						PointClusterMapping.put(entry.getKey(),j);
						}	
					}
				}

			}
		
		}

		return PointClusterMapping;
		


	}

	static Map<Integer,float[]> RecomputeCentroids(Map<String, Map<Integer,Float>> Articles ,Map<String,Integer> PointClusterMapping, int k){
		//Recompute Centroids
		Map<Integer,float[]> NewCentroids=new HashMap<Integer,float[]>();
		//get dimensions of all points belonging to the same cluster
		for(int i=0;i<k;i++){
			ArrayList<Map<Integer,Float>> Points=new ArrayList<Map<Integer,Float>>();
			for(Map.Entry<String, Integer> entry : PointClusterMapping.entrySet()){
				if(entry.getValue()==i){
					Points.add(Articles.get(entry.getKey()));
				}
			}
			float[] newCentroid=CalculateAverage(Points);
			NewCentroids.put(i,newCentroid);
		}
		return NewCentroids;
	} 

	static float CalculateEuclideanDistance(Map<Integer,Float> Point, float[] Centroid){
		float dist=0.0f;
		for(int i=0; i<5618;i++){
			if(Point.get(i)!=null){
				// System.out.println(Point.get(i)+" - "+Centroid[i]);
				dist+=Math.pow((Point.get(i)-Centroid[i]),2);
			}
			else{
				dist+=Math.pow(Centroid[i],2);
			}
		}

		return dist;
	}

	static float CalculateCosineSimilarity(Map<Integer,Float> Point, float[] Centroid){
		float numerator=0;
		float p1Square=0;
		float p2Square=0;
		for(int i=0;i<5618;i++){
			if(Point.get(i)!=null){
				numerator+=Point.get(i)*Centroid[i];
				p1Square+=Math.pow(Point.get(i),2);
			}
			p2Square+=Math.pow(Centroid[i],2);
		}
		return(numerator/(p1Square+p2Square));
	}

	static float[] CalculateAverage(ArrayList<Map<Integer,Float>> Points){
		float[] newCentroid=new float[5618];
		for(int i=0;i<5618;i++){
			float sum=0;
			for(Map<Integer,Float> point:Points){
				for(Map.Entry<Integer,Float> entry : point.entrySet()){
					if(entry.getKey()==i)
						sum+=entry.getValue();
				}
			}
			newCentroid[i]=sum/Points.size();
		}
		return newCentroid;
	}		float p1Square=0;


	static float ComputeSSE(Map<String,Integer> PointClusterMapping,Map<Integer,float[]> NewCentroids, Map<String, Map<Integer,Float>> Articles){
		float SSE=0;
		for(String key:PointClusterMapping.keySet()){
			SSE+=CalculateEuclideanDistance(Articles.get(key),NewCentroids.get(PointClusterMapping.get(key)));	
		}
		return SSE;
	}

	static float ComputeGlobalCosine(Map<String,Integer> PointClusterMapping,Map<Integer,float[]> NewCentroids, Map<String, Map<Integer,Float>> Articles){
		float GlobalCosine=0;
		for(String key:PointClusterMapping.keySet()){
			GlobalCosine+=CalculateCosineSimilarity(Articles.get(key),NewCentroids.get(PointClusterMapping.get(key)));	
		}
		return GlobalCosine;
	}



	static void ComputeEntropy(String ClassFile, Map<String,Integer> PointClusterMapping, int k){
		try{
			Map<String,String> ClassLabel =new HashMap<String,String>();
			String data = new String(Files.readAllBytes(Paths.get(ClassFile)));
			String[] lines=data.split("\n"); 
			for(String line:lines){
				String[] CLabels=line.split(",");
				ClassLabel.put(CLabels[0],CLabels[1]);
			}
			
			Map<Integer,Map<String,Integer>> EntropyTable=new HashMap<Integer,Map<String,Integer>>(); 

			for(String ArticleID:PointClusterMapping.keySet()){
				if(EntropyTable.get(PointClusterMapping.get(ArticleID))==null){
					//System.out.println("\nRan in 339  \n");
					//if cluster is not there crate cluster id and addd term
					Map<String,Integer> Term=new HashMap<String,Integer>();
					Term.put(ClassLabel.get(ArticleID),1);
					EntropyTable.put(PointClusterMapping.get(ArticleID),Term);
				}
				else{
					//if cluster existes and term is not there add term
					if(EntropyTable.get(PointClusterMapping.get(ArticleID)).get(ClassLabel.get(ArticleID))==null){
						//System.out.println("\nRan in 348 ");
						EntropyTable.get(PointClusterMapping.get(ArticleID)).put(ClassLabel.get(ArticleID),1);
					}
					//if cluster and term exist update count
					else{
						int count=0;
						
						count=EntropyTable.get(PointClusterMapping.get(ArticleID)).get(ClassLabel.get(ArticleID));
						//System.out.println("\nRan in 354  count: "+count);
						EntropyTable.get(PointClusterMapping.get(ArticleID)).put(ClassLabel.get(ArticleID),count+1);
					}	
				}

			}
		
			//Print clustering solution
			System.out.println("------------------------CLUSTERING SOLUTION-------------------------");
			for(Integer ClusterID:EntropyTable.keySet()){
				System.out.println("Cluster "+ClusterID);
				System.out.println("------------------------------");
				for(String term:EntropyTable.get(ClusterID).keySet()){
					System.out.println(term);
				}
				System.out.println();
				System.out.println();
				int total=0;
				for(String term:EntropyTable.get(ClusterID).keySet()){
					System.out.println(EntropyTable.get(ClusterID).get(term));
					total+=EntropyTable.get(ClusterID).get(term);
				}
				System.out.println();
				System.out.println("Total : "+total);
				
				System.out.println("------------------------------");
			}



			//calculate pij 
			int m=0;   //no of total points
			ArrayList<Integer> mjList=new ArrayList<Integer>();  //sizes of each clusters
			ArrayList<Float> ejList=new ArrayList<Float>();
			ArrayList<Float> purityList=new ArrayList<Float>();

			for(Integer ClusterID:EntropyTable.keySet()){
				int mj=0; //no of elements in each cluster
				for(String term: EntropyTable.get(ClusterID).keySet()){
					mj+=EntropyTable.get(ClusterID).get(term); 

				}
				mjList.add(mj);
				m+=mj;
				float ej=0f;
				float MaxPij=0f;

				for(String term: EntropyTable.get(ClusterID).keySet()){
					int mij=0;
					mij=EntropyTable.get(ClusterID).get(term);

					float pij=0;

					pij=(float)mij/mj;
					
					if(pij>MaxPij)
						MaxPij=pij;
					ej+=(float)pij*(Math.log(pij)/Math.log(2));	
					
				}

				purityList.add(MaxPij);

				ejList.add(ej);
			}

			float Entropy=0f;
			float Purity=0f;

			

			for(int i=0;i<k;i++){
				
				Entropy+=((float)mjList.get(i)/m)*(ejList.get(i));
				
				Purity+=((float)mjList.get(i)/m)*(purityList.get(i));
					
			}
			Entropy=-1+Entropy;
			System.out.println("Entropy: "+Entropy);
			System.out.println("Purity: "+Purity);

		}

		catch(Exception e){
			System.out.println(e);

		}
		 
	}

	

	static boolean CompareCentroids(Map<Integer,float[]> OldCentroids,Map<Integer,float[]>NewCentroids){
		boolean Same=true;
		for(int i=0;i<5618;i++){
			System.out.println("Hii");
			float[] OldCoord=OldCentroids.get(i);
			float[] NewCoord=NewCentroids.get(i);
			for(int j=0;j<OldCoord.length;i++){
				if(OldCoord[i]!=NewCoord[i])
				{
					Same=false;
					return Same;
				}

			}
		}
		return Same;
	}

	static boolean ComparePointMappinngs(Map<String,Integer> OldMapping,Map<String,Integer> NewMapping){
		// if(index==0){
		// 	return false;
		// }
		//System.out.println("Comparing");
		Boolean Equal=true;
		for(String keys: OldMapping.keySet()){
			if(OldMapping.get(keys)!=NewMapping.get(keys))
			{
				//System.out.println(keys);
				Equal=false;
				return Equal;
			}

		}	
		return Equal;
	}

	static Map<String,Integer> CopyPointMapping(Map<String,Integer> OldMapping){
		//System.out.println("Copying");
		Map<String,Integer> NewMapping=new HashMap<String,Integer>(); 
		for(String keys: OldMapping.keySet()){
			NewMapping.put(keys, OldMapping.get(keys));
		}
		return NewMapping;
	}

}






